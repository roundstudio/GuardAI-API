from transformers import YolosImageProcessor, YolosForObjectDetection
import torch
import cv2
from PIL import Image
import numpy as np
import threading
from queue import Queue
import os
import time
from multiprocessing import Process, Queue, Lock
import torch.multiprocessing as mp

class ObjectDetector:
    def __init__(self, model_path="hustvl/yolos-tiny"):
        import warnings
        warnings.filterwarnings("ignore")
        
        # غیرفعال کردن SSL verification
        os.environ['CURL_CA_BUNDLE'] = ''
        
        # فعال کردن CUDA بنچمارک برای عملکرد بهتر
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        self.processor = YolosImageProcessor.from_pretrained(
            model_path,
            ignore_mismatched_sizes=True,
            trust_remote_code=True,
            local_files_only=False
        )
        
        # استفاده از half precision در صورت پشتیبانی
        if torch.cuda.is_available():
            self.model = YolosForObjectDetection.from_pretrained(
                model_path,
                ignore_mismatched_sizes=True,
                torch_dtype=torch.float16,
                local_files_only=False
            ).to(self.device).half()
        else:
            self.model = YolosForObjectDetection.from_pretrained(
                model_path,
                ignore_mismatched_sizes=True,
                torch_dtype=torch.float32,
                local_files_only=False
            ).to(self.device)
        
        self.model.eval()
        
        # برگرداندن به سایز اصلی
        self.input_size = (640, 480)
        
        # حذف frame_queue و استفاده از یک متغیر مشترک
        self.latest_frame = None
        self.frame_lock = mp.Lock()
        self.result_queue = mp.Queue(maxsize=2)
        self.processing = True
        
        # کاهش threshold برای تشخیص سریعتر
        self.detection_threshold = 0.9  
        
        self.skip_frames = 2
        self.max_skip_frames = 5
        
        self.frame_buffer = []
        self.max_buffer_size = 2
        self.frame_count = 0
        
        # کش کردن نتایج
        self.result_cache = {}
        self.cache_timeout = 0.5  # نیم ثانیه

    @torch.inference_mode()
    def detect_objects(self, image, threshold=0.9):
        # بهینه‌سازی حافظه با حذف تصاویر قدیمی
        torch.cuda.empty_cache()
        
        inputs = self.processor(images=image, return_tensors="pt")
        # تبدیل نوع داده بر اساس دستگاه
        if torch.cuda.is_available():
            inputs = {k: v.to(self.device).half() for k, v in inputs.items()}
            target_sizes = torch.tensor([image.size[::-1]], dtype=torch.float16).to(self.device)
        else:
            inputs = {k: v.to(self.device).float() for k, v in inputs.items()}
            target_sizes = torch.tensor([image.size[::-1]], dtype=torch.float32).to(self.device)
        
        outputs = self.model(**inputs)
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=threshold
        )[0]
        return results

    def process_frames(self):
        while self.processing:
            self.frame_count += 1
            
            # رد کردن فریم‌های اضافی
            if self.frame_count % self.skip_frames != 0:
                continue
                
            with self.frame_lock:
                if self.latest_frame is None:
                    time.sleep(0.001)
                    continue
                frame = self.latest_frame.copy()
            
            # بررسی کش
            frame_hash = hash(frame.tobytes())
            current_time = time.time()
            
            if frame_hash in self.result_cache:
                cached_time, cached_results = self.result_cache[frame_hash]
                if current_time - cached_time < self.cache_timeout:
                    self.result_queue.put((frame, cached_results))
                    continue
            
            # پردازش فریم جدید
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            results = self.detect_objects(image)
            
            # ذخیره در کش
            self.result_cache[frame_hash] = (current_time, results)
            
            # حذف کش‌های قدیمی
            self.result_cache = {k: v for k, v in self.result_cache.items() 
                               if current_time - v[0] < self.cache_timeout}
            
            self.result_queue.put((frame, results))

    def start_processing(self):
        self.process = Process(target=self.process_frames)
        self.process.start()

    def preprocess_frame(self, frame):
        # کاهش نویز
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # تبدیل به grayscale برای تشخیص حرکت
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # اگر تغییر زیادی در صحنه نیست، پردازش را رد کن
        if hasattr(self, 'prev_frame'):
            diff = cv2.absdiff(gray, self.prev_frame)
            if diff.mean() < 5:  # threshold برای تشخیص تغییر
                return None
        
        self.prev_frame = gray
        return frame


import logging
from camera.models import Camera
from rule.models import Rule
from gpio.models import Gpio
from object_detection.models import UserObjectRequest
from utils.stream import IPCamera
import cv2
from utils.detector import ObjectDetector
import time
from concurrent.futures import ThreadPoolExecutor
import threading
from django.utils import timezone
import queue


# تنظیم لاگر
logging.basicConfig(
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# اضافه کردن StreamHandler برای نمایش در کنسول
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def process_camera(camera):
    window_name = f'Object Detection {camera.name}'
    
    ip_camera = IPCamera(
        ip_address=camera.ip, 
        username=camera.username, 
        password=camera.password, 
        port=camera.port,
        path=camera.path,
    )
    detector = ObjectDetector()

    processing_thread = threading.Thread(target=detector.process_frames)
    processing_thread.daemon = True
    processing_thread.start()

    if not ip_camera.connect('rtsp'):
        if not ip_camera.connect('http'):
            return

    ip_camera.start_stream()
    
    frame_skip = 1
    frame_count = 0
    last_process_time = time.time()
    min_process_interval = 0.05  # حداقل فاصله زمانی بین پردازش‌ها
    
    try:
        while True:
            frame = ip_camera.get_frame()
            if frame is None:
                continue
                
            current_time = time.time()
            if current_time - last_process_time < min_process_interval:
                continue
            
            # حذف فریم‌های قدیمی از صف
            while not detector.result_queue.empty() and detector.result_queue.qsize() > 1:
                try:
                    detector.result_queue.get_nowait()
                except:
                    break
            
            with detector.frame_lock:
                detector.latest_frame = frame
            
            if not detector.result_queue.empty():
                try:
                    processed_frame, results = detector.result_queue.get_nowait()
                    
                    active_rules = camera.rules.filter(status__in=['active', 'scheduled'])
                    
                    for rule in active_rules:
                        if rule.status == 'scheduled' and not rule.can_run_at_time(timezone.localtime()):
                            continue
                            
                        rule_objects = set(rule.object_types.values_list('name', flat=True))
                        
                        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                            if score >= rule.confidence_threshold:
                                object_name = detector.model.config.id2label[label.item()]
                                
                                if object_name in rule_objects:
                                    box = box.cpu().numpy()
                                    x1, y1, x2, y2 = map(int, box)
                                    
                                    if rule.priority == 1:
                                        color = (0, 255, 0)
                                    elif rule.priority == 2:
                                        color = (0, 255, 255)
                                    elif rule.priority == 3:
                                        color = (0, 165, 255)
                                    else:
                                        color = (0, 0, 255)
                                    
                                    cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
                                    text = f"{object_name} ({score:.2f})"
                                    cv2.putText(processed_frame, text, (x1, y1-10), 
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                                    
                                    for gpio in rule.gpio.all():
                                        logger.info(f"Detection: {object_name} (confidence: {score:.2f}) for rule: {rule.name} on GPIO Pin: {gpio.pin}")
                            
                    # نمایش مستقیم فریم بدون تاخیر اضافی
                    cv2.imshow(window_name, processed_frame)
                    cv2.waitKey(1)  # کاهش زمان انتظار
                    
                except queue.Empty:
                    continue
            
            last_process_time = current_time
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        logger.error(f"خطا در پخش دوربین {camera.name}: {str(e)}")
    finally:
        detector.processing = False
        processing_thread.join()
        ip_camera.disconnect()
        
    # فقط در انتها پنجره‌ها را ببند
    cv2.destroyAllWindows()

def process_database_task():
    # دریافت همه دوربین‌های فعال و زمان‌بندی شده
    active_cameras = []
    current_time = timezone.localtime()
    
    # دریافت قوانین فعال و زمان‌بندی شده
    rules = Rule.objects.filter(status__in=['active', 'scheduled'])
    
    for rule in rules:
        # برای قوانین زمان‌بندی شده، زمان را چک می‌کنیم
        if rule.status == 'scheduled' and not rule.can_run_at_time(current_time):
            continue
            
        cameras = rule.camera.all()
        active_cameras.extend(list(cameras))
    
    # حذف دوربین‌های تکراری
    active_cameras = list(set(active_cameras))
    
    logger.info(f"تعداد دوربین‌های فعال: {len(active_cameras)}")
    
    # پردازش همزمان دوربین‌ها
    with ThreadPoolExecutor(max_workers=min(len(active_cameras), 4)) as executor:
        futures = [executor.submit(process_camera, camera) for camera in active_cameras]
        
        # منتظر اتمام همه پردازش‌ها
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"خطا در پردازش دوربین: {str(e)}")





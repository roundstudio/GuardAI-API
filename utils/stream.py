import cv2
import numpy as np
from datetime import datetime
import time
import threading
import queue

class IPCamera:
    def __init__(self, ip_address=None, username=None, password=None, port=554, path=None):
        """
        راه‌اندازی اولیه کلاس دوربین IP
        
        Args:
            ip_address (str): آدرس IP دوربین
            username (str): نام کاربری
            password (str): رمز عبور
            port (int): پورت اتصال (پیش‌فرض RTSP: 554)
            path (str): مسیر دوربین
        """
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.port = port
        self.path = path
        self.stream = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=30)  # صف برای ذخیره فریم‌ها
        self.last_frame = None
        self.recording = False
        self.video_writer = None

    def build_stream_url(self, protocol='rtsp'):
        """ساخت URL جریان ویدیو"""
        if protocol.lower() == 'rtsp':
            return f"rtsp://{self.username}:{self.password}@{self.ip_address}:{self.port}/{self.path}"
        elif protocol.lower() == 'http':
            return f"http://{self.username}:{self.password}@{self.ip_address}:{self.port}/{self.path}"
        else:
            raise ValueError("پروتکل پشتیبانی نمی‌شود")

    def connect(self, protocol='rtsp'):
        """اتصال به دوربین"""
        try:
            stream_url = self.build_stream_url(protocol)
            self.stream = cv2.VideoCapture(stream_url)
            
            if not self.stream.isOpened():
                raise Exception("خطا در اتصال به دوربین")
            
            print("اتصال به دوربین با موفقیت برقرار شد")
            return True
            
        except Exception as e:
            print(f"خطا در اتصال به دوربین: {str(e)}")
            return False

    def disconnect(self):
        """قطع اتصال از دوربین"""
        if self.stream:
            self.stop_recording()
            self.is_running = False
            self.stream.release()
            print("اتصال دوربین قطع شد")

    def start_stream(self):
        """شروع دریافت جریان ویدیو در یک thread جداگانه"""
        self.is_running = True
        thread = threading.Thread(target=self._stream_thread)
        thread.daemon = True
        thread.start()

    def _stream_thread(self):
        """thread اصلی برای دریافت فریم‌ها"""
        while self.is_running:
            if self.stream and self.stream.isOpened():
                ret, frame = self.stream.read()
                if ret:
                    if self.frame_queue.full():
                        self.frame_queue.get()  # حذف قدیمی‌ترین فریم اگر صف پر است
                    self.frame_queue.put(frame)
                    self.last_frame = frame
                    
                    if self.recording and self.video_writer:
                        self.video_writer.write(frame)
                else:
                    print("خطا در خواندن فریم")
                    break
            time.sleep(0.01)  # تاخیر کوچک برای کاهش مصرف CPU

    def get_frame(self):
        """دریافت آخرین فریم"""
        return self.last_frame

    def start_recording(self, output_path=None):
        """شروع ضبط ویدیو"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"record_{timestamp}.mp4"

        if self.stream and self.stream.isOpened():
            fps = int(self.stream.get(cv2.CAP_PROP_FPS))
            width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            self.recording = True
            print(f"شروع ضبط ویدیو در {output_path}")

    def stop_recording(self):
        """توقف ضبط ویدیو"""
        if self.recording and self.video_writer:
            self.recording = False
            self.video_writer.release()
            self.video_writer = None
            print("ضبط ویدیو متوقف شد")

    def set_resolution(self, width, height):
        """تنظیم رزولوشن دوربین"""
        if self.stream:
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            print(f"رزولوشن به {width}x{height} تغییر کرد")

    def get_camera_info(self):
        """دریافت اطلاعات دوربین"""
        if self.stream and self.stream.isOpened():
            info = {
                "resolution": (
                    int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
                ),
                "fps": int(self.stream.get(cv2.CAP_PROP_FPS)),
                "codec": int(self.stream.get(cv2.CAP_PROP_FOURCC)),
                "ip_address": self.ip_address,
                "port": self.port
            }
            return info
        return None 
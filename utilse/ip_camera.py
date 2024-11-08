import cv2
import requests
import numpy as np
from typing import Optional

class IPCamera:
    """کلاس اصلی برای اتصال به دوربین‌های IP"""
    
    def __init__(self, ip: str, username: Optional[str] = None, 
                 password: Optional[str] = None, port: int = 8080, patch: Optional[str] = None):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.stream = None
        self.patch = patch
        
    def connect_rtsp(self) -> bool:
        """RTSP اتصال با استفاده از پروتکل"""
        try:
            url = f"rtsp://{self.username}:{self.password}@{self.ip}:{self.port}/{self.patch}"
            
            self.stream = cv2.VideoCapture(url)
            
            # تنظیمات بافر برای کاهش تاخیر
            self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # تنظیم کیفیت تصویر
            self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.stream.set(cv2.CAP_PROP_FPS, 30)
            
            is_opened = self.stream.isOpened()
            if not is_opened:
                print("نتوانست به دوربین متصل شود. لطفا آدرس RTSP را بررسی کنید.")
            else:
                print("اتصال موفقیت‌آمیز به دوربین")
            return is_opened
            
        except Exception as e:
            return False
            
    def connect_http(self) -> bool:
        """HTTP اتصال با استفاده از"""
        try:
            url = f"http://{self.ip}/video"
            if self.username and self.password:
                response = requests.get(url, auth=(self.username, self.password), stream=True)
            else:
                response = requests.get(url, stream=True)
            if response.status_code == 200:
                self.stream = response
                return True
            return False
        except Exception as e:
            print(f"خطا در اتصال HTTP: {str(e)}")
            return False
            
    def get_frame(self) -> Optional[np.ndarray]:
        """دریافت فریم از دوربین"""
        if self.stream is None:
            print("جریان ویدیو تعریف نشده است")
            return None
            
        try:
            # استفاده مستقیم از read به جای grab و retrieve
            ret, frame = self.stream.read()
            if ret:
                return frame
            else:
                print("نتوانست فریم را بخواند")
                return None
        except Exception as e:
            print(f"خطا در دریافت فریم: {str(e)}")
            return None
            
    def close(self):
        """بستن اتصال"""
        if self.stream:
            self.stream.release() 
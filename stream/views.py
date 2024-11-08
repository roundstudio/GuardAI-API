import cv2
from django.http import StreamingHttpResponse
from camera.models import Camera
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utilse.ip_camera import IPCamera
import RPi.GPIO as GPIO
import time

class StreamView(APIView):
    def generate_frames(self, ip_camera):
        while True:
            frame = ip_camera.get_frame()
            if frame is not None:
                # تبدیل فریم به فرمت JPEG با استفاده از OpenCV
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue  # در صورت خطا در انکودینگ، فریم را نادیده می‌گیریم
                
                # ارسال فریم JPEG
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    def get(self, request, cameraId):
        camera = Camera.objects.filter(is_active=True, id=cameraId)
        if not camera.exists():
            return Response({'error': 'No active cameras found'}, status=status.HTTP_404_NOT_FOUND)
        
        camera = camera.first()
        ip_camera = IPCamera(
            ip=camera.ip,
            username=camera.username,
            password=camera.password,
            port=camera.port,
            patch=camera.path
        )
        if not ip_camera.connect_rtsp():
            return Response({'error': 'Failed to connect to the camera'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # برگرداندن پاسخ به صورت استریم
        return StreamingHttpResponse(
            self.generate_frames(ip_camera),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )


class GpioView(APIView):
    def get(self, request,pin,durtion):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(durtion)
        GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()
        return Response({'message': f'{pin}, {durtion}'})

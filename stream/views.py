import cv2
from django.http import StreamingHttpResponse
from camera.models import Camera
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utilse.ip_camera import IPCamera
from rest_framework.permissions import IsAuthenticated
# import RPi.GPIO as GPIO
import time

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class StreamView(APIView):
    def generate_frames(self, ip_camera, fps=24):
        frame_interval = 1.0 / fps
        last_frame_time = 0
        
        while True:
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                continue

            frame = ip_camera.get_frame()
            if frame is not None:
                frame = cv2.resize(frame, (640, 480))
                ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not ret:
                    continue

                last_frame_time = current_time
                try:
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        jpeg.tobytes() + b'\r\n')
                except GeneratorExit:
                    # بستن اتصال در صورت خروج
                    ip_camera.close()
                    break



    def get(self, request, cameraId):
        # بررسی توکن
        # token = request.query_params.get('access_token')
        # if not token:
        #     return Response({'error': 'Authentication token missing'}, status=status.HTTP_401_UNAUTHORIZED)

        # try:
        #     # اعتبارسنجی توکن
        #     jwt_auth = JWTAuthentication()
        #     validated_token = jwt_auth.get_validated_token(token)
        #     user = jwt_auth.get_user(validated_token)
        #     self.check_permissions(request)
        # except AuthenticationFailed:
        #     return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        # ادامه کد
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

        response = StreamingHttpResponse(
            self.generate_frames(ip_camera),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )
        
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response


# class GpioView(APIView):
#     def get(self, request,pin,durtion):
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(pin, GPIO.OUT)
#         GPIO.output(pin, GPIO.HIGH)
#         time.sleep(durtion)
#         GPIO.output(pin, GPIO.LOW)
#         GPIO.cleanup()
#         return Response({'message': f'{pin}, {durtion}'})

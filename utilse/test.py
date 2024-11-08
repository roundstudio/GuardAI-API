import cv2
from ip_camera import IPCamera

# مثال استفاده
camera = IPCamera(
    ip="192.168.1.101",
    username="admin",
    password="admin",
    port=8080
)

# RTSP اتصال با
while camera.connect_rtsp():
    # دریافت و نمایش فریم
    frame = camera.get_frame()
    if frame is not None:
        cv2.imshow("Frame", frame)
        # کلید ESC برای خروج
        if cv2.waitKey(1) & 0xFF == 27:
            break

# بستن اتصال
camera.close()
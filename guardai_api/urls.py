from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from camera.views import CameraViewSet
from notification.views import NotificationViewSet
from alert.views import AlertViewSet
from stream.views import StreamView
# from stream.views import GpioView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'alerts', AlertViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/stream/<int:cameraId>/', StreamView.as_view(), name='stream'),
    # path('api/gpio/<int:pin>/<int:durtion>/', GpioView.as_view(), name='gpio'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]

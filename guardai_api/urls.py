from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from camera.views import CameraViewSet
from notification.views import NotificationViewSet
from stream.views import StreamView
from gpio.views import GpioView
from object_detection.views import UserObjectRequestList
from rule.views import RuleViewSet
from contact.views import ContactViewSet
from telegram.views import TelegramViewset

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'cameras', CameraViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'gpio', GpioView)
router.register(r'object-detection', UserObjectRequestList)
router.register(r'rule', RuleViewSet)
router.register(r'contact', ContactViewSet)
router.register(r'telegram', TelegramViewset)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/stream/<int:cameraId>/', StreamView.as_view(), name='stream'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

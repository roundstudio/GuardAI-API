from django.db import models
from camera.models import Camera
from object_detection.models import ObjectType
from gpio.models import Gpio
from django.core.validators import MinValueValidator, MaxValueValidator

class Rule(models.Model):
    STATUS_CHOICES = (
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('scheduled', 'زمانبندی شده'),
    )
    
    PRIORITY_CHOICES = (
        (1, 'کم'),
        (2, 'متوسط'),
        (3, 'زیاد'),
        (4, 'بحرانی'),
    )

    name = models.CharField(max_length=255, verbose_name="نام قانون")
    description = models.TextField(verbose_name="توضیحات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ به‌روزرسانی")
    
    # ارتباطات
    camera = models.ManyToManyField(Camera, related_name='rules', verbose_name="دوربین‌ها")
    object_types = models.ManyToManyField(ObjectType, related_name='rules', blank=True, verbose_name="انواع اشیاء")
    gpio = models.ManyToManyField(Gpio, related_name='rules', blank=True, verbose_name="پورت‌های GPIO")
    
    # تنظیمات اضافی
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="وضعیت")
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name="اولویت")
    
    # تنظیمات زمانی
    start_time = models.TimeField(null=True, blank=True, verbose_name="زمان شروع")
    end_time = models.TimeField(null=True, blank=True, verbose_name="زمان پایان")
    
    # تنظیمات تشخیص
    confidence_threshold = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="حد آستانه اطمینان"
    )
    detection_interval = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="فاصله زمانی تشخیص (ثانیه)"
    )
    
    # تنظیمات هشدار
    notification_cooldown = models.IntegerField(
        default=300,  # 5 دقیقه
        validators=[MinValueValidator(0)],
        verbose_name="زمان انتظار بین هشدارها (ثانیه)"
    )

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "قانون"
        verbose_name_plural = "قوانین"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def is_active(self):
        return self.status == 'active'

    def can_run_at_time(self, current_time):
        if not self.start_time or not self.end_time:
            return True
        return self.start_time <= current_time.time() <= self.end_time

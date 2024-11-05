from django.db import models
from django.contrib.postgres.fields import ArrayField
from camera.models import Camera
from notification.models import Notification

class Alert(models.Model):
    name = models.CharField(max_length=255)
    cameras = models.ManyToManyField(Camera)
    notifications = models.ManyToManyField(Notification)
    description = models.TextField()
    frequency_option = [
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    ]
    frequency = models.CharField(max_length=10, choices=frequency_option)
    days = ArrayField(
        models.IntegerField(),
        blank=True,
        null=True,
        help_text="If weekly, store days of the week (1-7); if monthly, store days of the month (1-31)"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    detection_option = [
        ('object', 'object'),
        ('animal', 'animal'),
        ('person', 'person'),
        ('vehicle', 'vehicle'),
    ]
    detection = models.CharField(max_length=10, choices=detection_option)


from django.db import models

class Notification(models.Model):
    name = models.CharField(max_length=255)
    Kind_Option = [
        ('GPIO', 'GPIO'),
    ]
    kind = models.CharField(max_length=4, choices=Kind_Option)
    duration = models.IntegerField(null=True , blank=True)
    username = models.CharField(max_length=100)
    pin = models.IntegerField()
    description = models.TextField()


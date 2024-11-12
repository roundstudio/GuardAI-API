from django.db import models

# Create your models here.
class Gpio(models.Model):
    name = models.CharField(max_length=255,unique=True)
    pin = models.IntegerField(unique=True)
    duration = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

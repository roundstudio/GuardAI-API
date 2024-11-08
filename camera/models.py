from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=255)
    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    path = models.CharField(max_length=255)
    description = models.TextField( null=True , blank=True)

    def __str__(self) -> str:
        return f'{self.name}'


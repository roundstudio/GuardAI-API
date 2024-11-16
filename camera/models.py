from django.db import models

class Camera(models.Model):
    name = models.CharField(max_length=255,unique=True)
    ip = models.GenericIPAddressField(unique=True)
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    path = models.CharField(max_length=255, null=True , blank=True)
    description = models.TextField( null=True , blank=True)

    def __str__(self) -> str:
        return f'<{self.name} - {self.ip} - {self.port} - {self.path} - {self.username} - {self.password}>'


from django.db import models

class Telegram(models.Model):
    token = models.CharField(max_length=255, verbose_name="توکن")
    chat_id = models.CharField(max_length=255, verbose_name="شناسه چت")
    name = models.CharField(max_length=255, verbose_name="نام")
    create_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField (default=True)
    def __str__(self) :
        return self.chat_id
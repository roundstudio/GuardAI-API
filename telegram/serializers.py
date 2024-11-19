from rest_framework import serializers
from .models import Telegram


class TelegramSerializers(serializers.ModelSerializer):
    class Meta:
        model = Telegram
        fields = '__all__'

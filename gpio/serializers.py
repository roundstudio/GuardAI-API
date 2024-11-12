from rest_framework import serializers
from .models import Gpio


class GpioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gpio
        fields = '__all__'


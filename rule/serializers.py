from rest_framework import serializers
from .models import Rule
from camera.serializers import CameraSerializer
from object_detection.serializers import ObjectTypeSerializer
from gpio.serializers import GpioSerializer

class RuleSerializer(serializers.ModelSerializer):
    camera_detail = CameraSerializer(source='camera', many=True, read_only=True)
    object_types_detail = ObjectTypeSerializer(source='object_types', many=True, read_only=True)
    gpio_detail = GpioSerializer(source='gpio', many=True, read_only=True)
    
    class Meta:
        model = Rule
        fields = '__all__'
        extra_fields = ['camera_detail', 'object_types_detail', 'gpio_detail'] 
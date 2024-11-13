from rest_framework import serializers
from .models import ObjectType, UserObjectRequest

class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = "__all__"
        extra_kwargs = {
            'name': {'validators': []}
        }

class UserObjectRequestSerializer(serializers.ModelSerializer):
    object_types = ObjectTypeSerializer(many=True)

    class Meta:
        model = UserObjectRequest
        fields = "__all__"

    def validate_object_types(self, value):
        # بررسی تکراری نبودن نام‌ها در داده‌های ورودی
        names = [item['name'] for item in value]
        if len(names) != len(set(names)):
            raise serializers.ValidationError("نام‌های تکراری در object_types مجاز نیست")
        return value

    def create(self, validated_data):
        object_types_data = validated_data.pop('object_types')
        user_request = UserObjectRequest.objects.create(**validated_data)
        for object_type_data in object_types_data:
            object_type, created = ObjectType.objects.get_or_create(**object_type_data)
            user_request.object_types.add(object_type)
        return user_request

    def update(self, instance, validated_data):
        object_types_data = validated_data.pop('object_types', [])
        
        # به‌روزرسانی سایر فیلدها
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # به‌روزرسانی object_types
        current_types = []
        for object_type_data in object_types_data:
            object_type, _ = ObjectType.objects.update_or_create(
                name=object_type_data['name'],
                defaults=object_type_data
            )
            current_types.append(object_type)
        
        # تنظیم object_types جدید
        instance.object_types.set(current_types)
        
        return instance

    def delete(self, instance):
        instance.object_types.clear()
        instance.delete()
from rest_framework import serializers
from .models import ObjectType, UserObjectRequest

class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = "__all__"

class UserObjectRequestSerializer(serializers.ModelSerializer):
    object_types = ObjectTypeSerializer(many=True)

    class Meta:
        model = UserObjectRequest
        fields = "__all__"

    def create(self, validated_data):
        object_types_data = validated_data.pop('object_types')
        user_request = UserObjectRequest.objects.create(**validated_data)
        for object_type_data in object_types_data:
            object_type, created = ObjectType.objects.get_or_create(**object_type_data)
            user_request.object_types.add(object_type)
        return user_request
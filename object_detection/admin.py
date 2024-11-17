from django.contrib import admin
from object_detection.models import ObjectType, UserObjectRequest
# Register your models here.
admin.site.register(ObjectType)
admin.site.register(UserObjectRequest)
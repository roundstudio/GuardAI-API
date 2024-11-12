from rest_framework import viewsets
from .models import Camera
from .serializers import CameraSerializer
from rest_framework.permissions import IsAuthenticated

class CameraViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer

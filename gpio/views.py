from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Gpio
from .serializers import GpioSerializer

# Create your views here.
class GpioView(viewsets.ModelViewSet):
    queryset = Gpio.objects.all()
    serializer_class = GpioSerializer
    # permission_classes = [IsAuthenticated]

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Telegram
from .serializers import TelegramSerializers
from rest_framework.permissions import IsAuthenticated


class TelegramViewset (viewsets.ModelViewSet):
    queryset = Telegram.objects.all()
    serializer_class = TelegramSerializers
    # permission_classes = [IsAuthenticated]


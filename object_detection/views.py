from django.shortcuts import render
from rest_framework import viewsets
from .models import UserObjectRequest
from .serializers import UserObjectRequestSerializer

# Create your views here.


class UserObjectRequestList(viewsets.ModelViewSet):
    queryset = UserObjectRequest.objects.all()
    serializer_class = UserObjectRequestSerializer

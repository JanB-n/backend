from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
# Create your views here.

# from rest_framework import viewsets

# from .serializers import UserSerializer
# from .models import User


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all().order_by('last_name')
#     serializer_class = UserSerializer

from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addUser(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

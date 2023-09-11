from django.shortcuts import render
from pymongo.mongo_client import MongoClient
from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
import json
from bson import json_util
# Create your views here.

connection_string = 'mongodb+srv://9baran:ArcyWrog@cluster0.hmiq5.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(connection_string)

db = client['Relacs']

compounds = db["compounds"]

JWT_authenticator = JWTAuthentication()

# Create your views here.

# @api_view(['GET'])
# def getUsers(request):
#     users = User.objects.all()
#     serializer = UserSerializer(users, many=True)
#     return Response(serializer.data)

# @api_view(['POST'])
# def addUser(request):
#     serializer = UserSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#     return Response(serializer.data)

class CompoundView(APIView): 
    def post(self, request, format='json'):
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            print(request.data)
            user = User.objects.get(id=request.user.id)
            #request.data['id_user'] = user 
            newdata = request.data
            newdata['id_user'] = user.pk
            # if serializer.is_valid(raise_exception = True):
            #     compound = serializer.save()
            #     if compound:
            #         json = serializer.data
            #         return Response(json, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            try:
                compounds.insert_one(newdata)
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        if userVerified is not None:
            compound_list = []
            for compound in compounds.find({"id_user": request.user.id}):
                compound_list.append(compound)
            compounds_serialized = json_util.dumps(compound_list)
            print(compounds_serialized)
            #compounds_serialized = serializers.serialize('json', compounds)
            #json.loads(compounds_serialized)
            #print(json.loads(compounds_serialized)[0])
            return Response(json.loads(compounds_serialized), content_type="application/json")
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)

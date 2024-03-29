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
from bson.objectid import ObjectId
from . import helpers
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

class CompoundsView(APIView): 
    def post(self, request, format='json'):
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            
            user = User.objects.get(id=request.user.id)
            #request.data['id_user'] = user 
            newdata = request.data
            newdata['id_user'] = user.pk
            
            newdata['measurements'] = []
            # if serializer.is_valid(raise_exception = True):
            #     compound = serializer.save()
            #     if compound:
            #         json = serializer.data
            #         return Response(json, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            if 'name' in newdata and 'molar_mass' in newdata:
                if newdata['name'] != "" and newdata['molar_mass'] != "" and '+' not in newdata['name'] and '-' not in newdata['name']:
                    try:
                        newdata['molar_mass'] = float(newdata['molar_mass'])
                        compounds.insert_one(newdata)
                        return Response(status=status.HTTP_201_CREATED)
                    except:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        if userVerified is not None:
            try:
                compound_list = []
                for compound in compounds.find({"id_user": request.user.id}):
                    compound_list.append(compound)
                compounds_serialized = json_util.dumps(compound_list)
                
                return Response(json.loads(compounds_serialized), content_type="application/json")
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def delete(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('id')
        if userVerified is not None:
            try: 
                compounds.delete_one({"_id":  ObjectId(id)})
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        
class CompoundView(APIView):
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('id')
        if userVerified is not None:
            try:
                document = compounds.find_one({'_id': ObjectId(id)})
                document_serialized = json_util.dumps(document)
                
                if document is not None:
                    return Response(json.loads(document_serialized), content_type="application/json")
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request):
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            try:
            
                full_data = request.data['measurements']
                probe_mass = float(request.data['probe_mass'])
                field_epsilon = 1
                tmp_epsilon = 0.05
                file_name =  request.data['file_name']
                document = compounds.find_one({'_id': ObjectId(request.data['comp_id'])})
                ###
                if document['id_user'] != response[1]['user_id']:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                ###
                molar_mass = float(document['molar_mass'])
                data = helpers.get_data_from_csv(full_data)
                data = helpers.calculate_additional_measurements(data, molar_mass, probe_mass)
                clusterized_data = helpers.clusterize(data, field_epsilon, tmp_epsilon)
                measurements = []
                for cluster in clusterized_data:
                    for measurement in cluster:
                        measurements.append(helpers.measurize(measurement, file_name, field_epsilon, tmp_epsilon))
                
                document_serialized = json_util.dumps(document)
                document = json.loads(document_serialized)
                merged_measurements = []
                if 'measurements' in document != [] :
                    saved_measurements = document['measurements']
                    for new_measurement in measurements:
                        theSame = False
                        i = 0
                        for document_measurement in document['measurements']:
                            if new_measurement['name'] == document_measurement['name']:
                                theSame = True
                                saved_measurements[i]['df'] = new_measurement['df'].to_json() 
                                saved_measurements[i]['edited'] = False   
                            i += 1                   
                        if theSame == False:
                            new_measurement['df'] = new_measurement['df'].to_json()
                            saved_measurements.append(new_measurement)
                    compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": saved_measurements}})
                else:
                    compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": measurements}})
                document = compounds.find_one({'_id': ObjectId(request.data['comp_id'])})
                document_serialized = json_util.dumps(document)
                document = json.loads(document_serialized)
                    
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class MeasurementsView(APIView):
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('id')
        if userVerified is not None:
            try:
                #measurements = list(compounds.find({'_id': ObjectId(id)}, {"measurements": 1, "_id": 0}))
                document = compounds.find_one({'_id': ObjectId(id)})
                if document is not None:
                    if document['id_user'] == userVerified[1]['user_id']:
                        return Response({'measurements': document['measurements'], 'currentUser': userVerified[1]['user_id'], 'isUserAdmin': True}, content_type="application/json")
                    else:
                        return Response({'measurements': document['measurements'], 'currentUser': userVerified[1]['user_id'], 'isUserAdmin': False}, content_type="application/json")

                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def delete(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('id')
        if userVerified is not None:
            try:
                print("aaa")
                document = compounds.find_one({"_id": ObjectId(id)})
                print(document['id_user'] != userVerified[1]['user_id'])
                
                compounds.update_one({"_id":  ObjectId(id)},{"$set":{"measurements": []}})
                
            
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)

class MeasurementView(APIView):
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        if userVerified is not None:
            try:
                id = request.GET.get('c_id')
                measurement_id = request.GET.get('m_id')
                measurement_id = measurement_id.replace('__', ':').replace('%', ' ').replace('--', '.')
                document = compounds.find_one({'_id': ObjectId(id)})
                
               
                if document is not None:
                    measurement = helpers.getMeasurement(document, measurement_id)
                    if measurement is not None:
                        print(document['id_user'] == userVerified[1]['user_id'])
                        if document['id_user'] == userVerified[1]['user_id']:
                            return Response({'measurement': measurement, 'isUserAdmin': True}, content_type="application/json")
                        else:
                            return Response({'measurement': measurement, 'isUserAdmin': False}, content_type="application/json")
                    else:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def put(self, request):
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            
            try:
                comp_id = request.data['c_id']
                measurement_id = request.data['m_id']
                new_measurement = request.data['newDf']
                document = compounds.find_one({"_id":  ObjectId(comp_id)})
                ###
                if document['id_user'] != response[1]['user_id']:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                ###
                measurements = document['measurements']
                for measurement in measurements:
                    if measurement['name'] == measurement_id:
                        measurement['df'] = new_measurement
                        measurement['edited'] = True

                compounds.update_one({"_id":  ObjectId(comp_id)},{"$set":{"measurements": measurements}})
                #compounds.insert_one(newdata)
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def delete(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('comp_id')
        measurement_name = request.GET.get('measurement_name')
        if userVerified is not None:
            try:
                document = compounds.find_one({"_id":  ObjectId(id)})
                if document['id_user'] != userVerified[1]['user_id']:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
                print("msname", measurement_name, id)
                measurements = document['measurements']
                measurements = [measurement for measurement in measurements if not (measurement['name'] == measurement_name)]
                compounds.update_one({"_id":  ObjectId(id)},{"$set":{"measurements": measurements}})
                
            
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
class SharedCompoundsView(APIView):
    def put(self, request):
        response = JWT_authenticator.authenticate(request)
        if response is not None: 
            try:
                id = request.data['id']
                print(id, request.GET)
                document = compounds.find_one({"_id":  ObjectId(id)})
                isShared = 0
                user = User.objects.get(id=document['id_user'])
                username = user.username
                if 'shared' in document:
                    if document['shared'] == 1:
                        isShared = 0
                    elif document['shared'] == 0:
                        isShared = 1
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    
                else:
                    isShared = 1

                compounds.update_one({"_id":  ObjectId(id)},{"$set":{"shared": isShared, "owner_username": username}})
                #compounds.insert_one(newdata)
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        if userVerified is not None:
            try:
                compound_list = []
                for compound in compounds.find({"shared": 1}):
                    compound_list.append(compound)
                compounds_serialized = json_util.dumps(compound_list)
                
                return Response(json.loads(compounds_serialized), content_type="application/json")
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request, format='json'):
        response = JWT_authenticator.authenticate(request)
        if response is not None:
            try:
                user_id = response[1]['user_id']
                id = request.data['id']
                document = compounds.find_one({"_id":  ObjectId(id)})
                document['id_user'] = user_id
                document['shared'] = 0
                del document['_id']
                compounds.insert_one(document)
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        else:
            print("no token is provided in the header or the header is missing")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
class CurrentUserView(APIView):
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        if userVerified is not None:
            try:
                return Response(json.loads({'current_user': userVerified[1]['user_id'], }), content_type="application/json")
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
        
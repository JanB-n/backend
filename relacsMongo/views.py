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
            print(request.data)
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
            try:
                compound_list = []
                for compound in compounds.find({"id_user": request.user.id}):
                    compound_list.append(compound)
                compounds_serialized = json_util.dumps(compound_list)
                # print(compounds_serialized)
                #compounds_serialized = serializers.serialize('json', compounds)
                #json.loads(compounds_serialized)
                #print(json.loads(compounds_serialized)[0])
                return Response(json.loads(compounds_serialized), content_type="application/json")
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            print("User not verified")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
class CompoundView(APIView):
    def get(self, request):
        userVerified = JWT_authenticator.authenticate(request)
        id = request.GET.get('id')
        if userVerified is not None:
            try:
                document = compounds.find_one({'_id': ObjectId(id)})
                document_serialized = json_util.dumps(document)
                # print(document)
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
            # print(request.data['measurements'])
            # with open('df.txt', 'w') as f:
            #     f.write(json.dumps(request.data['measurements']))
            # if serializer.is_valid(raise_exception = True):
            #     compound = serializer.save()
            #     if compound:
            #         json = serializer.data
            #         return Response(json, status=status.HTTP_201_CREATED)
            # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if True:
            # try:
            
                full_data = request.data['measurements']
                probe_mass = float(request.data['probe_mass'])
                field_epsilon = 1
                tmp_epsilon = 0.05
                file_name =  request.data['file_name']
                document = compounds.find_one({'_id': ObjectId(request.data['comp_id'])})
                molar_mass = float(document['molar_mass'])
                data = helpers.get_data_from_csv(full_data)
                data = helpers.calculate_additional_measurements(data, molar_mass, probe_mass)
                clusterized_data = helpers.clusterize(data, field_epsilon, tmp_epsilon)
                measurements = []
                for cluster in clusterized_data:
                    for measurement in cluster:
                        print(measurement)
                        measurements.append(helpers.measurize(measurement, file_name, field_epsilon, tmp_epsilon))
                
                # for measurement in measurements:
                #     measurement['df'] = measurement['df'].to_json()
                #     print(measurement['df'])
                
                # for one_measurement in full_data:
                #     one_measurement = {key: one_measurement[key] for key in ['Temperature (K)', 'Magnetic Field (Oe)', "AC X' (emu/Oe)", "AC X'' (emu/Oe)", "AC Frequency (Hz)"]}
                #     data.setdefault((round(one_measurement['Temperature (K)'], 1), round(one_measurement['Magnetic Field (Oe)'], 1)), []).append(one_measurement)

                # for key, value in data.items():
                #     measurement_collection = {}
                #     measurement_collection['temperature'] = key[0]
                #     measurement_collection['field'] = key[1]
                #     measurement_collection['name'] = f'T: {key[0]}K H: {key[1]}e'
                #     measurement_collection['measurements_local'] = value
                #     measurements.append(measurement_collection)

                document_serialized = json_util.dumps(document)
                document = json.loads(document_serialized)
                # if 'measurements' in document:
                #     #new_measurements = helpers.mergeLists(document['measurements'], measurements)
                #     #compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": new_measurements}})
                #     #compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": {}}})
                #     compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": measurements}})
                # else:
                #     compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": measurements}})
                # document = compounds.find_one({'_id': ObjectId(request.data['comp_id'])})
                # document_serialized = json_util.dumps(document)
                # document = json.loads(document_serialized)

                # with open('document.json', 'w') as f:
                #     f.write(json.dumps(measurements))
                
                if 'measurements' in document != [] :
                    saved_measurements = document['measurements']
                    for new_measurement in measurements:
                        theSame = False
                        for document_measurement in document['measurements']:
                            if new_measurement['name'] == document_measurement['name']:
                                theSame = True
                        if theSame == False:
                            new_measurement['df'] = new_measurement['df'].to_json()
                            saved_measurements.append(new_measurement)
                    compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": saved_measurements}})
                else:
                    compounds.update_one({"_id":  ObjectId(request.data['comp_id'])},{"$set":{"measurements": measurements}})
                print('calculated')
                document = compounds.find_one({'_id': ObjectId(request.data['comp_id'])})
                document_serialized = json_util.dumps(document)
                document = json.loads(document_serialized)

                with open('document.json', 'w') as f:
                    f.write(json.dumps(document))
            try:        
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
                measurements = list(compounds.find({'_id': ObjectId(id)}, {"measurements": 1, "_id": 0}))
                #document_serialized = json_util.dumps(document)
                # print(document)
                if measurements is not None:
                    return Response(measurements[0]['measurements'], content_type="application/json")
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
            #try:
                compounds.update_one({"_id":  ObjectId(id)},{"$set":{"measurements": []}})
                #document_serialized = json_util.dumps(document)
                # print(document)
            
                return Response(status=status.HTTP_204_NO_CONTENT)
            #except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
    
        
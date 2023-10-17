from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
# from .models import User


class Register(APIView):

    def post(self, request, format='json'):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception = True):
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def auth(request):
#     try:
#         user = User.objects.get(email=request.data['email'])
#         serializer = UserSerializer(user)
#         return Response(serializer.data)
#     except User.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
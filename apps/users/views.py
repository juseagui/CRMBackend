from datetime import datetime
#from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate
#from apps.base.api import GeneralListApiView

from rest_framework.response import Response
#from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.api.serializers import CustomTokenObtainPairSerializer, CustomUserSerializer
from apps.users.models import User

#Aut con JWT
class Login(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username','')
        password = request.data.get('password','')
        user = authenticate(
            username = username,
            password = password
        )

        if user:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                user_serializer = CustomUserSerializer(user)
                return Response({
                    'token' : login_serializer.validated_data.get('access'),
                    'refresh_token' : login_serializer.validated_data.get('refresh'),
                    'user' : user_serializer.data,
                    'message' : 'Ok'
                }, status=status.HTTP_200_OK)
            return Response({'error':'NOT_VALID_USER'} ,  status = status.HTTP_400_BAD_REQUEST)
        return Response({'error':'LOGIN_ERROR'} ,  status = status.HTTP_400_BAD_REQUEST)

class Logout (GenericAPIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.filter(id=request.data.get('user',0))
        if user.exists():
            RefreshToken.for_user(user.first())
            return  Response({'message':'Login Ok'} ,  status = status.HTTP_200_OK)
        return Response({'error':'Not exist user'} ,  status = status.HTTP_400_BAD_REQUEST)


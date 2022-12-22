
from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.users.api.serializers import CustomTokenObtainPairSerializer, CustomUserSerializer, ChangePasswordSerializer
from apps.users.models import User

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid

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

# -------------------------------------------------------------------------------------------------
# Controller to manage user password
# -------------------------------------------------------------------------------------------------

class UserAccessViewSet (viewsets.ModelViewSet):
    serializer_class = ChangePasswordSerializer
    model = User
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def create(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        data_serializer = self.get_serializer( data = request.data )

        if data_serializer.is_valid():
            # Check old password
            if not self.object.check_password(request.data.get("old_password")):
                return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': "Wrong password",
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
            
            # set_password also hashes the password that the user will get
            self.object.set_password(request.data.get("new_password"))
            self.object.save()
            
            return Response( {'cid' : str(uuid.uuid4()),
                        'status' : 'success',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [] }, status = status.HTTP_200_OK )

    
        return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': data_serializer.errors,
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

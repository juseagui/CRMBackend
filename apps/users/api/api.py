from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from apps.users.api.serializers import CustomUserSerializer as UserSerializer , TestUserSerializer, UserListSerializer
from apps.users.models import User

"""class UserAPIView( APIView ):
    def get(self,request):
        user = User.objects.all()
        users_serializer = UserSerializer( user, many= True )
        return Response( users_serializer.data )"""

@api_view(['GET','POST'])
def user_api_view( request ):
    
    #list
    if request.method == 'GET':
        user = User.objects.all().values('id','username','email','password','name')
        users_serializer = UserListSerializer( user, many= True )

        #-----------------------------forma no model
        
        """test_data = {
            'name' : 'develop',
            'email' : 'prueba@hotmail.com'

        }

        test_user = TestUserSerializer( data = test_data )
        #print( TestUserSerializer( data = request.data) )
        if test_user.is_valid():
            user_instance = test_user.save()
            print(user_instance)
            print('paso validacion') """

        #-----------------------------------------

        return Response( users_serializer.data , status = status.HTTP_200_OK )
    
    #created
    elif request.method == 'POST':
        #print( request.data )
        users_serializer = UserSerializer(data = request.data )
        
        #validation
        if users_serializer.is_valid():
            users_serializer.save()
            return Response( { 'message' : 'Se creo exitosamente', 'data' : users_serializer.data }  , status = status.HTTP_201_CREATED )
        return Response( users_serializer.errors , status = status.HTTP_400_BAD_REQUEST )


@api_view(['GET','PUT','DELETE'])
def user_api_detail_view( request, pk ):

    #queryset
    user = User.objects.filter( id = pk ).first()
    
    #validacion
    if user:

        #retrive
        if request.method == 'GET':
            
            users_serializer = UserSerializer( user )
            return Response( users_serializer.data )
        
        #update
        elif request.method == 'PUT':
            users_serializer = UserSerializer( user, data = request.data )
            
            if users_serializer.is_valid():
                users_serializer.save()
                return Response( users_serializer.data, status = status.HTTP_200_OK )
            else:
                return Response( users_serializer.errors,  status = status.HTTP_400_BAD_REQUEST )

        #delete
        elif request.method == 'DELETE':
            user.delete()
            return Response( { 'message' : 'Usuario eliminado Correctamente' } , status = status.HTTP_200_OK )

    return Response( { 'message' : 'No se h encontrado usuario con esos datos' },  status = status.HTTP_400_BAD_REQUEST )
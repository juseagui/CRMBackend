from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.users.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass

class CustomUserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create( self, validate_data):
        user = User(**validate_data)
        user.set_password( validate_data['password'] )
        user.save()
        return user
    
    def update( self, instance, validate_data):
        upsate_user = super().update(instance,validate_data)
        upsate_user.set_password( validate_data['password'] )
        upsate_user.save()
        return upsate_user


class UserListSerializer( serializers.ModelSerializer ):
    class Meta:
        model = User

    def to_representation( self,instance ):
        return{
            'id' : instance['id'],
            'username' : instance['username'],
            'email' : instance['email']
            #'password' : instance['password']
        }
    


class TestUserSerializer ( serializers.Serializer ):
    name = serializers.CharField(max_length = 255)
    email = serializers.EmailField()

    def validate_name(self, value):
        print( value )
        return value

    def validate_email(self, value):
        print( value )
        return value

    def validate(self, value):
        return value

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.email = validated_data.get('email',instance.email)
        instance.save()
        return instance

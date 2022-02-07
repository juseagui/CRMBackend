from rest_framework import serializers
from apps.objects.models import Field, Object, Group


class ObjectSerializer (serializers.ModelSerializer):
    #Funcionalidad que permite retornar los datos de foraneas

    class Meta:
        model = Object
        exclude  = ('state','created_date','modified_date','deleted_date' )  

class ObjectCustomSerializer (serializers.ModelSerializer):
    #fields = serializers.StringRelatedField( many=True )
    class Meta:
        model = Object
        fields  = ('id','name','description','icon', 'view', 'model') 

class GroupCustomSerializer (serializers.ModelSerializer):
     class Meta:
        model = Group
        fields  = ('id','name','order','state')


class FieldSerializer (serializers.ModelSerializer):
    object_field = ObjectCustomSerializer()


    class Meta:
        model = Field
        exclude  = ('created_date','modified_date','deleted_date' )  

class FieldCaptureSerializer (serializers.ModelSerializer):
    object_group = GroupCustomSerializer()

    class Meta:
        model = Field
        exclude  = ('created_date','modified_date','deleted_date' )  
    
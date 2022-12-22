from rest_framework import serializers
from apps.objects.models import Field, Object, Group, List, ValueList, CategoryObject, Permission , Relationship


# ------------------------------------------------------------
#-------- SERIALIZERS PERMISSIONS
#--------------------------------------------------------------

class FilteredPermissionSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(  state=True, rol_permission__id = self.context['request'].user.rol_user.id  ).order_by('id')
        #data = data.filter(  state=True, object_rol__isnull = True ).order_by('sort')
        return super(FilteredPermissionSerializer, self).to_representation(data)

class PermissionSerializer (serializers.ModelSerializer):
     class Meta:
        list_serializer_class = FilteredPermissionSerializer
        model = Permission
        exclude  = ('created_date','modified_date','deleted_date' ) 

class ObjectPermissionsSerializer (serializers.ModelSerializer):
    #category_object = CategoryObjectSerializer()
    object_rol = PermissionSerializer(many=True)
    class Meta:
        model = Object
        exclude  = ('created_date','modified_date','deleted_date' )
        #depth = 1

class CategoryObjectSerializer (serializers.ModelSerializer):
    category_object = ObjectPermissionsSerializer( many=True )

    class Meta:
        model = CategoryObject
        exclude  = ('created_date','modified_date','deleted_date' )
        

# ------------------------------------------------------------
#-------- SERIALIZERS CORE 
#--------------------------------------------------------------


class ObjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = Object
        exclude  = ('state','created_date','modified_date','deleted_date' )


class ObjectCustomSerializer (serializers.ModelSerializer):
    #fields = serializers.StringRelatedField( many=True )
    class Meta:
        model = Object
        fields  = ('id','model','representation','name','description','icon') 

class GroupCustomSerializer (serializers.ModelSerializer):
     class Meta:
        model = Group
        fields  = ('id','name','sort','state')

class ValueListSerializer (serializers.ModelSerializer):
     class Meta:
        model = ValueList
        exclude  = ('created_date','modified_date','deleted_date' ) 

class ListSerializer (serializers.ModelSerializer):
     ListValues = ValueListSerializer(many=True)
     class Meta:
        model = List
        exclude  = ('created_date','modified_date','deleted_date' ) 

class RelationshipSerializer (serializers.ModelSerializer):
    class Meta:
        model = Relationship
        exclude  = ('state','created_date','modified_date','deleted_date' )





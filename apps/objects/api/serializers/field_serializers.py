from rest_framework import serializers
from apps.objects.models import Field

#import dependency serializers
from apps.objects.api.serializers.object_serializers import ObjectCustomSerializer,GroupCustomSerializer, ListSerializer


class FieldSerializer (serializers.ModelSerializer):
    class Meta:
        model = Field
        exclude  = ('created_date','modified_date','deleted_date' )


class FieldVisibleSerializer (serializers.ModelSerializer):
    object_field = ObjectCustomSerializer()

    class Meta:
        model = Field
        ordering = ['sort']
        exclude  = ('created_date','modified_date','deleted_date' )  


class FieldCaptureSerializer (serializers.ModelSerializer):
    object_field = ObjectCustomSerializer()
    object_group = GroupCustomSerializer()
    object_list = ListSerializer()
    object_relationship = ObjectCustomSerializer()
    class Meta:
        model = Field
        exclude  = ('created_date','modified_date','deleted_date' )  

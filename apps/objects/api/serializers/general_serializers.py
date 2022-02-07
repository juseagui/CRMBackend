from rest_framework import serializers

from apps.objects.models import CategoryObject,Group,Field


class CategoryObjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = CategoryObject
        exclude = ('state','created_date','modified_date','deleted_date')


class GroupobjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ('state','created_date','modified_date','deleted_date')
        

class FieldobjectSerializer (serializers.ModelSerializer):
    class Meta:
        model = Field
        exclude = ('state','created_date','modified_date','deleted_date')
        
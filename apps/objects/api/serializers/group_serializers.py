from rest_framework import serializers
from apps.objects.models import Group

class GroupCustomSerializer (serializers.ModelSerializer):
     class Meta:
        model = Group
        exclude  = ('state','created_date','modified_date','deleted_date' )


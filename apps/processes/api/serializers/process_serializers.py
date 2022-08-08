from rest_framework import serializers
from apps.processes.models import Process, Activity

#import dependency serializers
from apps.objects.api.serializers.object_serializers import ObjectCustomSerializer

class ActivitySerializer (serializers.ModelSerializer):
   class Meta:
      model = Activity
      exclude  = ('created_date','modified_date','deleted_date' ) 

class ProcessCustomSerializer (serializers.ModelSerializer):
   object_process = ObjectCustomSerializer()
   processActivity = ActivitySerializer (many=True)
   
   class Meta:
      model = Process
      exclude  = ('state','created_date','modified_date','deleted_date' )

class ProcessSerializer (serializers.ModelSerializer):
   class Meta:
      model = Process
      exclude  = ( 'state','created_date','modified_date','deleted_date' )

  
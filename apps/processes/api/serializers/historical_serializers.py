from rest_framework import serializers
from apps.processes.models import HistoricalProcess

class HistoricalSerializer (serializers.ModelSerializer):
   class Meta:
      model = HistoricalProcess
      exclude  = ('created_date','modified_date','deleted_date' ) 
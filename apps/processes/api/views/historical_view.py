#package rest_framework
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

#import serializers
from apps.processes.api.serializers.historical_serializers import HistoricalSerializer

#package personality querys bd and mixins
from apps.processes.mixins.validateProcess_mixins import validateProcess

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid

# -------------------------------------------------------------------------------------------------
# Controller to manage the data history
# -------------------------------------------------------------------------------------------------

class HistoricalViewSet( viewsets.ModelViewSet ):
    serializer_class = HistoricalSerializer
    http_method_names = ['post']
    permission_classes = (IsAuthenticated,)

    def create( self, request ):

        serializer = self.get_serializer( data=request.data )
        
        if ( serializer.is_valid() ):
            #update previous record
            validateProcessData = validateProcess( request.data["object_historical"], request.user.id, request.data["process_historical"], None )
            dataProcess = validateProcessData.endOldActivities( request.data["id_record"]  )
            serializer.save()

            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],}, status = status.HTTP_201_CREATED )
           
        else:
            return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': serializer.errors,
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )



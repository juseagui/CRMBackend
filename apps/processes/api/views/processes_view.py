#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import connection

#import serializers
from apps.processes.api.serializers.process_serializers import ProcessCustomSerializer, ProcessSerializer

from apps.processes.models import  Activity

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid
import re

# -------------------------------------------------------------------------------------------------
# Controller to manage the process flow 
# -------------------------------------------------------------------------------------------------

class ProcessViewSet( viewsets.ModelViewSet ):
    serializer_class = ProcessSerializer
    http_method_names = ['get','post','patch','put']
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self, pk= None):
        if pk:
            self.serializer_class = ProcessCustomSerializer
        
        return self.serializer_class

    def get_queryset( self, pk = None):
        if pk:
            return self.get_serializer().Meta.model.objects.get( id = pk )
        else:
            return self.get_serializer().Meta.model.objects.filter( state = True )

    def list( self, request):

        #define serializer work
        self.get_serializer_class()

        data_process = self.get_serializer( self.get_queryset(), many = True )

        return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : data_process.data }, status = status.HTTP_200_OK )

    def retrieve( self, request, pk=None):

        #define serializer work
        self.get_serializer_class( pk )
        
        try:
            processData = self.get_serializer( self.get_queryset( pk ) )
        
            return Response( {'cid' : str(uuid.uuid4()),
                        'status' : 'success',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : processData.data }, status = status.HTTP_200_OK )
        
        except self.get_serializer().Meta.model.DoesNotExist:
            
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'Not exist item',
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
  
    def partial_update(self, request, pk=None):

        data = request.data
        dataNew = dict()   

        #update header process
        try:
            processData = self.get_queryset( pk )
            dataNew['description'] = data.get('description')
            dataNew['object_process'] = data.get('object_process')
            
            serializerResult = self.serializer_class( processData, data = dataNew )
           
            if serializerResult.is_valid():
                serializerResult.save()

                #if the process is saved, the activities are processed
                listActivities = data.get('processActivity')

                try:
                    for itemActivity in list(listActivities):
                        Activity.objects.update_or_create(
                            code = itemActivity.get('code'), 
                            process_activity = processData,
                            defaults={
                                'code': itemActivity.get('code'), 
                                'sort' : itemActivity.get('sort'),
                                'description' : itemActivity.get('description'),
                                'process_activity' : processData,
                                },
                        )

                except Exception as e:
                    return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error':  str(e),
                            'detailError' : [] }, status = status.HTTP_500_INTERNAL_SERVER_ERROR )


                return Response( {'cid' : str(uuid.uuid4()),
                        'status' : 'success',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [] }, status = status.HTTP_200_OK )
            
            else:
                return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': serializerResult.errors,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

        
        except self.get_serializer().Meta.model.DoesNotExist:
            
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'Not exist item',
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
    
    def create( self, request):

        data = request.data
        dataNew = dict()   

        dataNew['description'] = data.get('description')
        dataNew['object_process'] = data.get('object_process')

        serializer = self.serializer_class( data = dataNew )

        if serializer.is_valid():
            processData = serializer.save()
            
            listActivities = data.get('processActivity')

            try:
                for itemActivity in list(listActivities):
                    Activity.objects.create(
                        code = itemActivity.get('code'), 
                        process_activity = processData,
                        description = itemActivity.get('description'),
                        sort = itemActivity.get('sort'),
                        )

            except Exception as e:
                return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error':  str(e),
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

            return Response( {'cid' : str(uuid.uuid4()),
                        'status' : 'success',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [] }, status = status.HTTP_200_OK )
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'Not exist item',
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
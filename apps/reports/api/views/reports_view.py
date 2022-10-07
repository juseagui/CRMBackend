#package rest_framework
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

#package personality querys bd and mixins
from apps.reports.mixins.models.generateReports_mixins import ReportModelRaw

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid


class ReportsProcessViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get']
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        typeReport = pk
        dataReport = None
        modelReport = ReportModelRaw()

        if(typeReport == 'stateProcess'):
            dataReport = modelReport.getStateProcess()
        elif(typeReport == 'stateProcessValue'):
            dataReport = modelReport.getStateValueProcess()
        elif(typeReport == 'stateCountProcess'):
            dataReport = modelReport.getStateCountProcess()

        if( dataReport.status == 'OK' ):
            return Response( {'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : dataReport.data }, status = status.HTTP_200_OK )
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': dataReport.msg,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )


class ReportsProgramViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get']
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        typeReport = pk
        dataReport = None
        modelReport = ReportModelRaw()

        if(typeReport == 'stateProgram'):
            dataReport = modelReport.getStateProgram()
       
        if( dataReport.status == 'OK' ):
            return Response( {'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : dataReport.data }, status = status.HTTP_200_OK )
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': dataReport.msg,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

    

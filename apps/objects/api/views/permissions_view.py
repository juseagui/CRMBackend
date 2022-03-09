#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import connection

from apps.objects.api.serializers.object_serializers import CategoryObjectSerializer

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw
from apps.objects.mixins.validateField_mixins import validateField

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid


# -----------------------------------------------------------------------------------------------------
# Get Permisions categoris and object
# -- router : objectsPermissions
#------------------------------------------------------------------------------------------------------

class objectsPermissionsCustomViewSet( viewsets.ModelViewSet ):
    serializer_class = CategoryObjectSerializer
    http_method_names = ['get']
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get_queryset( self, pk = None ):
       return self.get_serializer().Meta.model.objects.filter(state= True)

    def list( self, request):
        object_serializer = self.get_serializer( self.get_queryset(), many = True )

        return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : object_serializer.data }, status = status.HTTP_200_OK )
#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import connection

from apps.objects.api.serializers.object_serializers import ObjectSerializer, RelationshipSerializer
from apps.objects.api.serializers.field_serializers import FieldSerializer
from apps.objects.api.serializers.group_serializers import GroupCustomSerializer
from apps.objects.models import  Field, Relationship

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid
import re


# -------------------------------------------------------------------------------------------------
# Controller to manage the object master
# -------------------------------------------------------------------------------------------------

class ObjectViewSet( viewsets.ModelViewSet ):
    serializer_class = ObjectSerializer
    http_method_names = ['get','post','patch','put']
    permission_classes = (IsAuthenticated,)
    
    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.filter( state = True ).order_by('sort')

    def list( self, request):
        object_serializer = self.get_serializer( self.get_queryset(), many = True )

        return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : object_serializer.data }, status = status.HTTP_200_OK )

    def create( self, request):
        #validate model
        patron = re.compile("^\w+$")
        if( patron.match(request.data["model"]) ):
            serializer = self.serializer_class( data = request.data, context={'request': '/objects'} )
            if serializer.is_valid():

                modelRawObject = ObjectModelRaw()

                #check if the table exists
                dataTable = modelRawObject.getTableSystem( request.data["model"] )
                transacSuccess = True
                
                #if it doesn't exist create it
                if(not dataTable.data):
                    responseCreatedTable = modelRawObject.postTableSystem( request.data["model"] ) 
                    if( responseCreatedTable.status != 'OK' ):
                        transacSuccess = False

                if( transacSuccess ):
                    serializer.save()

                    if(serializer.data):
                        if(serializer.data['id']):

                            #create group
                            firstGroup = dict()
                            firstGroup['name'] = 'Información principal'
                            firstGroup['object_group'] = serializer.data['id']
                            firstGroup['sort'] = 1

                            serializerGroup = GroupCustomSerializer( data = firstGroup )
                            if serializerGroup.is_valid():
                                serializerGroup.save()

                                #create field id
                                firstField = dict()
                                firstField['name'] = 'id'
                                firstField['description'] = 'id'
                                firstField['type'] = 5
                                firstField['type_relation'] = 1
                                firstField['sort'] = 1
                                firstField['object_field'] = serializer.data['id']
                                firstField['object_group'] = serializerGroup.data['id']
                                firstField['visible'] = '1'
                                firstField['capture'] = '0'
                                firstField['detail'] = '0'
                                firstField['edit'] = '0'
                                firstField['required'] = '1'
                                firstField['number_charac'] = 11
                                firstField['columns'] = 3

                                serializerField = FieldSerializer( data = firstField )

                                if serializerField.is_valid():
                                    serializerField.save()

                    return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'success',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],}, status = status.HTTP_201_CREATED )

                else:
                    return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'error',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],
                                'error': responseCreatedTable.msg,
                                'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
            
            return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'error',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],
                                'error': serializer.errors,
                                'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'The model is invalid or incorrect - '+request.data["model"],
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

    def update( self,request,pk=None ):

        object = self.get_queryset().filter(id = pk).first()
        if object:
            object.state = False
            object.save()
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],}, status = status.HTTP_200_OK )

        return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': 'Not found',
                        'detailError' : [] }, status = status.HTTP_404_NOT_FOUND )


# -------------------------------------------------------------------------------------------------
# Controller to manage object relationships
# -------------------------------------------------------------------------------------------------

class RelationshipViewSet( viewsets.ModelViewSet ):
    serializer_class = RelationshipSerializer
    http_method_names = ['get','post','patch']
    permission_classes = (IsAuthenticated,)

    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.get( 
                id = pk
            )

    def retrieve( self, request, pk=None):
        
        #get parameter to filter by visible value
        filterVisible = None if self.request.query_params.get('visible') not in ["1","0"] else self.request.query_params.get('visible')
        
        #get relation in field
        dataRelation = Field.objects.filter(
            type_relation= 2, object_relationship = pk
            ).values(
                'object_field'
            ).annotate(
                description_object = F('object_field__description'),
                name_object = F('object_field__name'),
                icon_object = F('object_field__icon'),
                name_object_parent = F('object_relationship__name'),
                icon_object_parent = F('object_relationship__icon')
            )
        

        if( list(dataRelation) ):
            # get relationship available
            relationshipAva = Relationship.objects.filter( 
                object_parent = pk, state = True
                ).values(
                    'id', 'object_parent' , 'object_child', 'description', 'visible'
                )
            
            jsonData = []
            for itemObject in list(dataRelation):
                itemFielTemp = dict()
                found = False
                for itemRelation in list(relationshipAva):
                    if( itemObject.get('object_field') == itemRelation.get('object_child') ):
                        found = True
                        itemFielTemp['description'] = itemRelation.get('description')
                        itemFielTemp['object_parent'] = itemRelation.get('object_parent')
                        itemFielTemp['object_parent_name'] = itemObject.get('name_object_parent')
                        itemFielTemp['object_parent_icon'] = itemObject.get('icon_object_parent')
                        itemFielTemp['object_child'] = itemRelation.get('object_child')
                        itemFielTemp['object_child_name'] = itemObject.get('name_object')
                        itemFielTemp['object_child_icon'] = itemObject.get('icon_object')
                        itemFielTemp['visible'] =  '0' if ( itemRelation.get('visible') == None or itemRelation.get('visible') == '0' ) else '1' 
                        itemFielTemp['object_parent_descrip'] = itemObject.get('description_object')
                        itemFielTemp['id_relationship'] = itemRelation.get('id')
                        
                if( not found ):
                    itemFielTemp['description'] = ""
                    itemFielTemp['object_parent'] = pk
                    itemFielTemp['object_parent_name'] = itemObject.get('name_object_parent')
                    itemFielTemp['object_parent_icon'] = itemObject.get('icon_object_parent')
                    itemFielTemp['object_child'] = itemObject.get('object_field')
                    itemFielTemp['object_child_name'] = itemObject.get('name_object')
                    itemFielTemp['object_child_icon'] = itemObject.get('icon_object')
                    itemFielTemp['visible'] = '0'
                    itemFielTemp['object_parent_descrip'] = itemObject.get('description_object')
                    itemFielTemp['id_relationship'] = None
                        
                #Validate filter patrams visible
                if(filterVisible is None):
                    jsonData.append(itemFielTemp)
                else:
                    if(itemFielTemp['visible'] == filterVisible ):
                        jsonData.append(itemFielTemp)


            return Response( {'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : jsonData }, status = status.HTTP_200_OK )

        else:

            return Response( {'cid' : str(uuid.uuid4()),
                            'status' : 'success',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : {} }, status = status.HTTP_200_OK )
       
    def create( self, request):
       
        data = request.data
        success = 0
        error = 0
        msgError = []

        for itemRelation in list(data):
            
            data = dict()   

            try:
                relationshipAva = self.get_queryset( itemRelation.get('id_relationship') )

                #if it exists it is updated
                data['description'] = itemRelation.get('description')
                data['object_parent'] = itemRelation.get('object_parent')
                data['object_child'] = itemRelation.get('object_child')
                data['visible'] = itemRelation.get('visible')

                serializer = self.serializer_class( relationshipAva, data = data )

                if serializer.is_valid():
                    serializer.save()
                    success =+ success
                else:
                    error += 1
                    msgError.append(serializer.errors)
            
            except self.get_serializer().Meta.model.DoesNotExist:

                #if it does not exist it is created
                data['description'] = itemRelation.get('description')
                data['object_parent'] = itemRelation.get('object_parent')
                data['object_child'] = itemRelation.get('object_child')
                data['visible'] = itemRelation.get('visible')
                
                serializer = self.serializer_class( data = data )

                if serializer.is_valid():
                    serializer.save()
                    success =+ success
                else:
                    error += 1
                    print(serializer.errors)
                    msgError.append(serializer.errors)
                    

        if( error > 0):
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'Relationship validation error',
                            'detailError' : msgError }, status = status.HTTP_400_BAD_REQUEST )

        else:
            return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : {} }, status = status.HTTP_200_OK )
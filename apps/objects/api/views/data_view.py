
#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import connection

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw
from apps.objects.mixins.validateField_mixins import validateField

#package bd django
from django.db.models import F
from datetime import datetime
import uuid

#import models
from apps.objects.models import  Field


# -------------------------------------------------------------------------------------------------
# Controller to manage the data of the various objects
# -------------------------------------------------------------------------------------------------

class DataObjectCustomViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get','post','patch']
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        # Get data field for list datalist
        data = Field.objects.filter( 
            object_field = pk
             ).values(
                'name','type','sort','visible', 'type_relation', 'object_list_id','object_relationship_id'
                ).annotate( 
                    model = F('object_field__model')).order_by('sort')
        
        #get parameter if you want to filter by object relationship
        parentRelationship = self.request.query_params.get('parentRelationship')
        pkParentRelationship = self.request.query_params.get('pkParentRelationship')

        # process data for get data in the object DB model
        if list(data):
            modelDefault = list(data)[0].get('model')
            modelAlias = modelDefault+"_"+pk
            nameField = ""
            join = ""
            
            #get field type relation = pk
            if (list(data)[0].get('type_relation') == 1 ):
                pkField =  list(data)[0].get('name')

            conditional = ""
            foundRelationship = False
            
            for itemField in list(data):
                
                #get data only visible is true
                if( itemField.get('visible') == '1' ):
                    nameFieldBD = itemField.get('name')
                    
                    #validate relation for List
                    if( itemField.get('type') == 7 and itemField.get('object_list_id') != None ):
                        nameField += "valuelist_"+nameFieldBD+".description "+nameFieldBD
                        join += " LEFT JOIN objects_valuelist valuelist_"+nameFieldBD+" "
                        join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = " + str(itemField.get('object_list_id'))
                    else: 
                        nameField += modelAlias+"."+nameFieldBD

                    nameField += ","

                    if( parentRelationship != None and pkParentRelationship != None ):
                        #Validate if there is an object relationship to filter the information
                        if ( itemField.get('object_relationship_id') == int(parentRelationship) ):
                            conditional += nameFieldBD+" = "+pkParentRelationship
                            foundRelationship = True
            
            if( parentRelationship != None and pkParentRelationship != None ):
                if( not foundRelationship ):
                    return Response({'cid' : str(uuid.uuid4()),
                                    'status' : 'error validate relationship filter data',
                                    'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                    'data' : [],
                                    'error': 'parentRelationship - '+parentRelationship+' Not found in module configuration id '+pk,
                                    'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
                            
            #get params for pagination
            offset = self.request.query_params.get('offset') if self.request.query_params.get('offset') != None else 0
            limit = self.request.query_params.get('limit') if self.request.query_params.get('limit') != None else 15

            modelRawObject = ObjectModelRaw()

            #quitar caracter ","
            if( nameField[-1] == "," ):
                nameField = nameField[:-1]

            #get count data of model
            responseCountDataObject = modelRawObject.getCountDataObject( modelDefault, conditional )
            #get data of model
            responseDataObject = modelRawObject.getDataObject( modelDefault, modelAlias, nameField, offset, limit, pkField, None, None, join, conditional  )
            
            #validate Response
            if(responseDataObject.status == 'OK'):
                
                respAditional = {
                'count' : responseCountDataObject.data[0]['count'],
                'data' : responseDataObject.data
                }

                return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : respAditional }, status = status.HTTP_200_OK )

        return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error validate fields',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': 'Object '+pk+' does not exist, not active or has no fields',
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

    def create(self, request):
        idObje = self.request.query_params.get('object')
        data = request.data
        
        if(idObje != None):
            
            dataObject = Field.objects.filter( 
            object_field = idObje
                ).values(
                'name','type','sort', 'type_relation', 'capture', 'required', 'number_charac'
                ).annotate( 
                    model = F('object_field__model')).order_by('sort')
            
            if(dataObject):
                validateFieldData = validateField(idObje, dataObject)
                validateFieldData.validateListField(data)

                if not validateFieldData.getFieldError():
                    modelRawObject = ObjectModelRaw()
                    
                    #insert new data in the model
                    responsePostDataObject = modelRawObject.postDataObject( validateFieldData.getModel(), 
                                                                                validateFieldData.getStringInsert(),
                                                                                validateFieldData.getStringValues() )

                    if(responsePostDataObject.status == 'OK'):
                        return Response( {'cid' : str(uuid.uuid4()),
                                            'status' : 'sucess',
                                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                            'data' : [] }, status = status.HTTP_201_CREATED )
                    else:
                        return Response( {'cid' : str(uuid.uuid4()),
                                            'status' : 'error database',
                                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                            'data' : [],
                                            'error': 'error in query' ,
                                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
                
                else:
                    return Response( {'cid' : str(uuid.uuid4()),
                                        'status' : 'error validate fields',
                                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                        'data' : [],
                                        'error': 'error in validate' ,
                                        'detailError' : validateFieldData.getFieldError() }, status = status.HTTP_400_BAD_REQUEST )

            else:
                return Response( {'cid' : str(uuid.uuid4()),
                                    'status' : 'error validate fields',
                                    'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                    'data' : [],
                                    'error': 'object not valid' ,
                                    'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST ) 
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error validate fields',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'param object is required' ,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

    def partial_update(self,  request, pk = None,):
        
        idObje = self.request.query_params.get('object')
        data = request.data

        if(idObje != None):
            
            dataObject = Field.objects.filter( 
            object_field = idObje
             ).values(
                'name','type','sort', 'type_relation', 'capture', 'required', 'number_charac'
                ).annotate( 
                    model = F('object_field__model')).order_by('sort')

            if(dataObject):
                validateFieldData = validateField(idObje, dataObject)
                validateFieldData.validateListField(data)
            
                if not validateFieldData.getFieldError():
                        modelRawObject = ObjectModelRaw()
                        
                        #insert new data in the model
                        responseUpdateDataObject = modelRawObject.updateDataObject( validateFieldData.getModel(), 
                                                                                validateFieldData.getStringUpdate(),
                                                                                validateFieldData.getPkName(),
                                                                                pk )

                        if(responseUpdateDataObject.status == 'OK'):
                            return Response( {'cid' : str(uuid.uuid4()),
                                              'status' : 'sucess',
                                              'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                              'data' : [] }, status = status.HTTP_204_NO_CONTENT )
                        else:
                            return Response( {'cid' : str(uuid.uuid4()),
                                            'status' : 'error database',
                                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                            'data' : [],
                                            'error': 'error in query' ,
                                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
                else:   
                    return Response( {'cid' : str(uuid.uuid4()),
                                        'status' : 'error validate fields',
                                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                        'data' : [],
                                        'error': 'error in validate' ,
                                        'detailError' : validateFieldData.getFieldError() }, status = status.HTTP_400_BAD_REQUEST )
            else:
                return Response( {'cid' : str(uuid.uuid4()),
                                  'status' : 'error validate fields',
                                  'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                  'data' : [],
                                  'error': 'object not valid' ,
                                  'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
        else:
            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error validate fields',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'param object is required' ,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )


# -------------------------------------------------------------------------------------------------
# Controller to manage data related objects
# -------------------------------------------------------------------------------------------------

class DataObjectRelationshipCustomViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        # var pk is idobject
        # Get data field for list datalist
        data = Field.objects.filter( 
            object_field = pk, visible = '1'
             ).values(
                'name','type','sort','visible', 'type_relation', 'object_list_id'
                ).annotate( 
                    model = F('object_field__model')).order_by('sort')

        return Response({'cid' : str(uuid.uuid4()),
                        'status' : 'error validate fields',
                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                        'data' : [],
                        'error': 'Object '+pk+' does not exist, not active or has no fields',
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )


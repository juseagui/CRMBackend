#package rest_framework
from lib2to3.pgen2.token import EQUAL
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import connection

from apps.objects.api.serializers.field_serializers import FieldSerializer , FieldCaptureSerializer, FieldVisibleSerializer
from apps.objects.models import Object,Field

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw
from apps.objects.mixins.models.field_model import FieldModelRaw
from apps.processes.mixins.validateProcess_mixins import validateProcess

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid


# -----------------------------------------------------------------------------------------------------
# Custom Field Get and Create 
# -- router : field
# -- params: visible 
#------------------------------------------------------------------------------------------------------

class FieldViewSet( viewsets.ModelViewSet ):
    serializer_class = FieldSerializer
    http_method_names = ['get','post','patch','put']
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):

        if(self.request.query_params.get('visible')):
            self.serializer_class = FieldVisibleSerializer
        elif(self.request.query_params.get('capture')):
            self.serializer_class = FieldCaptureSerializer
        else:
            return self.serializer_class

        return self.serializer_class
    
    def get_queryset( self, pk = None, method = 'GET' ):
        
        #define serializer work
        self.get_serializer_class()
        
        if method == 'PATCH' or method == 'PUT':
            return self.get_serializer().Meta.model.objects.get( 
                id = pk
            )

        #filters query
        visible = self.request.query_params.get('visible')
        capture = self.request.query_params.get('capture')
        idObject = self.request.query_params.get('object')

        if( visible ):
            return self.get_serializer().Meta.model.objects.filter( 
                object_field = idObject, 
                visible = visible,
                state = 1
            ).order_by('sort')

        elif(capture):
            action = self.request.query_params.get('action')

            if(action == 'edit'):
                return self.get_serializer().Meta.model.objects.filter( 
                    object_field = idObject, 
                    state = 1,
                ).order_by('object_group__sort','sort')
            else:
                return self.get_serializer().Meta.model.objects.exclude(
               type_relation = 1
            ).filter(
                object_field = idObject, 
                capture = capture,
                state = 1,
            ).order_by('object_group__sort','sort')
     
    def list(self, request):
        idObject = self.request.query_params.get('object')
        fieldObject = self.get_queryset( idObject )
        # Query Get Fields of object
        dataReturn = self.get_serializer( fieldObject, many = True ).data

        capture = self.request.query_params.get('capture')
        action = self.request.query_params.get('action')
        pkModel = self.request.query_params.get('pk')

        # Validate if the product has a parameterized process
        validateProcessData = validateProcess( idObject, request.user.id, None,  pkModel )
        dataProcess = validateProcessData.validateExistProcessObject()

        if(capture and action == 'edit' and pkModel):
            data = list(dataReturn)
            #begin process action edit
            if data[0]:
                object = data[0].get('object_field')
                modelDefault = object.get('model')
                modelAlias = modelDefault+"_"+idObject
                representation = object.get('representation')
                nameField = ""
                join = ""
                countData = len(data)
                interator = 0
                
                #get field type relation = pk
                if (data[0].get('type_relation') == 1 ):
                    #validate ERROR when is null
                    pkName = data[0].get('name')

                for itemField in data:
                        nameFieldBD = itemField.get('name')
                    
                        #validate relation for List
                        if( itemField.get('type') == 7 and itemField.get('object_list').get('id') != None ):
                            nameField += "valuelist_"+nameFieldBD+".description "+nameFieldBD
                            nameField += ","+modelAlias+"."+nameFieldBD+" code_"+nameFieldBD
                            join += " LEFT JOIN objects_valuelist valuelist_"+nameFieldBD+" "
                            join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = " + str(itemField.get('object_list').get('id'))
                        else: 
                            nameField += modelAlias+"."+nameFieldBD

                        interator += 1
                        if(interator != countData):
                            nameField += ","

                modelRawObject = ObjectModelRaw()
                #get data of model
                responseDataObject = modelRawObject.getDataObject( modelDefault, modelAlias, nameField, None, None, pkName, pkModel, representation, join )
                
                if( responseDataObject.data != None ):

                    jsonData = []
                    for itemFieldValue in data:
                        #exclude pk if not detail
                        if(itemFieldValue.get('capture') == '1'):
                            itemFielTemp = itemFieldValue
                            #create list temp
                            if(itemFieldValue.get('type') == 7):
                                valueObject = { 'description' : responseDataObject.data[0].get(itemFieldValue.get('name')),
                                                'code'        :  str(responseDataObject.data[0].get("code_"+itemFieldValue.get('name')))   }
                            else:
                                valueObject = responseDataObject.data[0].get(itemFieldValue.get('name'))
                            
                            itemFielTemp['value'] = valueObject
                            itemFielTemp['representation'] = responseDataObject.data[0].get(representation)
                            #add value in json
                            jsonData.append(itemFielTemp)
                
                else:
                    return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'error',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],
                                'error': 'The Query is None',
                                'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

            historical = []
            #validate actual activity
            if dataProcess:
                historical = validateProcessData.validateExistHistoricalProcess( True )

            #final process action edit
            respAditional = {
                'created_date' : responseDataObject.data[0].get('created_date'),
                'modified_date' : responseDataObject.data[0].get('modified_date'),
                'process' : {
                    'activities' : dataProcess,
                    'historical' : historical
                } ,
                'data' : jsonData
            }
        
        else:
            respAditional = {
                'process' : {
                    'activities' : dataProcess,
                    'historical' : []
                } ,
                'data' : dataReturn
            }

        return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : respAditional }, status = status.HTTP_200_OK )

    def retrieve(self, request, pk=None):
        # Get data field for list datalist
        #get params for detail
        idObje = self.request.query_params.get('object') if self.request.query_params.get('object') != None else 0

        #validate params object
        if idObje != 0:
            
            #Get data field and object
            data = Field.objects.filter( 
                    ( Q(detail='1') |  Q(type_relation='1')  ), object_field = idObje
                ).values(
                    'name','description', 'type','sort','visible','detail', 'type_relation' , 
                    'object_group','required', 'columns', 'number_charac', 'object_list_id','object_relationship_id'
                    ).annotate( 
                        model = F('object_field__model'),
                        representation = F('object_field__representation'),
                        group_name = F('object_group__name'),
                        object_relationship_model = F('object_relationship__model'),
                        object_relationship_rep = F('object_relationship__representation')
                    ).order_by('object_group__sort','sort')
            
            # process data for get data in the object DB model
            if list(data)[0]:
                modelDefault = list(data)[0].get('model')
                modelAlias = modelDefault+"_"+pk
                representation = list(data)[0].get('representation')
                nameField = ""
                join = ""
                
                #get field type relation = pk
                if (list(data)[0].get('type_relation') == 1 ):
                    #validate ERROR when is null
                    pkName =  list(data)[0].get('name')
                

                for itemField in list(data):
                    nameFieldBD = itemField.get('name')
                
                    #validate relation for List
                    if( itemField.get('type') == 7 and itemField.get('object_list_id') != None ):
                        nameField += "valuelist_"+nameFieldBD+".description "+nameFieldBD
                        nameField += ","+modelAlias+"."+nameFieldBD+" code_"+nameFieldBD
                        join += " LEFT JOIN objects_valuelist valuelist_"+nameFieldBD+" "
                        join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = "+ str(itemField.get('object_list_id'))

                    #validate relation for object
                    elif( itemField.get('object_relationship_id') != None and itemField.get('object_relationship_rep') != None ):
                        nameField += itemField.get('object_relationship_model')+"."+itemField.get('object_relationship_rep')+" AS "+nameFieldBD+", "
                        nameField += modelAlias+"."+nameFieldBD+" AS "+"code_"+nameFieldBD
                        join += " LEFT JOIN "+itemField.get('object_relationship_model')
                        join += " ON "+itemField.get('object_relationship_model')+".id = "+modelAlias+"."+nameFieldBD

                    else: 
                        nameField += modelAlias+"."+nameFieldBD

                    nameField += ","

                modelRawObject = ObjectModelRaw()

                #remove character ","
                if( nameField[-1] == "," ):
                    nameField = nameField[:-1]
                
                #get data of model
                responseDataObject = modelRawObject.getDataObject( modelDefault, modelAlias, nameField, None, None, pkName, pk, representation, join )
                
                if( responseDataObject.data != None ):

                    jsonData = []
                    arrGroup = dict()
                    for itemFieldValue in list(data):
                        #exclude pk if not detail
                        if(itemFieldValue.get('detail') == '1'):
                            itemFielTemp = itemFieldValue
                            #create list temp
                            arrGroup['id'] = itemFielTemp['object_group']
                            arrGroup['name'] = itemFielTemp['group_name']
                            itemFielTemp['value'] = responseDataObject.data[0].get(itemFieldValue.get('name'))
                            itemFielTemp['code'] = responseDataObject.data[0].get("code_"+itemFieldValue.get('name'))
                            itemFielTemp['representation'] = responseDataObject.data[0].get(itemFieldValue.get('representation'))
                            itemFielTemp['object_group'] = arrGroup
                            #add value in json
                            jsonData.append(itemFielTemp)
                            arrGroup = dict()

                    #validate Response
                    if(responseDataObject.status == 'OK'):

                        # Validate if the product has a parameterized process
                        validateProcessData = validateProcess( idObje, request.user.id, None, pk )
                        dataProcess = validateProcessData.validateExistProcessObject()
                        historical = []

                         #validate actual activity
                        if dataProcess:
                            historical = validateProcessData.validateExistHistoricalProcess()
                        
                        respAditional = {
                            'created_date' : responseDataObject.data[0].get('created_date'),
                            'modified_date' : responseDataObject.data[0].get('modified_date'),
                            'process' : {
                                'activities' : dataProcess,
                                'historical' : historical
                            } ,
                            'data' : jsonData
                        }

                        return Response( {'cid' : str(uuid.uuid4()),
                                        'status' : 'success',
                                        'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                        'data' : respAditional }, status = status.HTTP_200_OK )
                    else:
                        return Response({'cid' : str(uuid.uuid4()),
                                    'status' : 'error validate fields',
                                    'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                    'data' : [],
                                    'error': responseDataObject.msg ,
                                    'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

                else:
                    return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'error',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],
                                'error': 'The Query is None',
                                'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

        
        return Response({'cid' : str(uuid.uuid4()),
                                'status' : 'error',
                                'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                'data' : [],
                                'error': 'param object required',
                                'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

    def create(self, request):
        
        data = request.data
        serializer = self.serializer_class( data = request.data )

        if serializer.is_valid():

            #create field in table BD
            name = data["name"]
            type = data["type"]
            number_charac = data["number_charac"]
            required = data["required"]
            idObje = data["object_field"]

            #Alter table
            #Get data object
            dataObject = Object.objects.filter( 
                    id = idObje
                ).values(
                    'name','view', 'model'
                )
            
            modelRawField = FieldModelRaw()

            if list(dataObject)[0]:
                model = list(dataObject)[0].get('model')

                """
                # Definition Data Type
                -- 1. Texto
                -- 2.Email
                -- 3.Texto Largo
                -- 4. Fecha 
                -- 5. Numero
                -- 6. Decimal
                -- 7. List
                """
                if( type == 4 ):
                    typeDescription = "DATE"
                    number_charac = None
                elif( type == 5 ):
                    typeDescription = "INT"
                elif( type == 6 ):
                    typeDescription = "DECIMAL"
                else:
                    typeDescription = "VARCHAR"

                if (required =='1'):
                    nullable = 'NOT NULL'
                else:
                    nullable = 'NULL'


            responseDataField = modelRawField.upsertColumnTable( model, "ADD", name, typeDescription, number_charac, nullable )

            #Validate if error is duplicate column
            if ( "Duplicate column" in responseDataField.msg ):
                responseDataField = modelRawField.upsertColumnTable( model, "MODIFY COLUMN", name, typeDescription, number_charac, nullable )

            if( responseDataField.status == 'OK' ):
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
                        'error': responseDataField.msg,
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

        return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': serializer.errors,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )
        
    def partial_update(self, request, pk=None):
        
        data = request.data
        idObje = data["object_field"]
        
        #Get data object
        dataObject = Field.objects.filter( 
                object_field = idObje , id = pk
            ).values(
                'name','type','required','number_charac'
            ).annotate( 
                    model = F('object_field__model'),
            )
        
        if list(dataObject):
            #create field in table BD
            name = data["name"]
            type = data["type"]
            number_charac = data["number_charac"]
            required = data["required"]

            dataAccesObject = list(dataObject)[0]
            model = dataAccesObject.get('model')

            #validate that the name is not altered
            name = dataAccesObject.get('name') if name != dataAccesObject.get('name') else name
            request.data["name"] = name
      
            serializer = self.serializer_class( self.get_queryset(pk, 'PATCH'), data = request.data )

            if serializer.is_valid():
                
                modelRawField = FieldModelRaw()

                """
                # Definition Data Type
                -- 1. Texto
                -- 2.Email
                -- 3.Texto Largo
                -- 4. Fecha 
                -- 5. Numero
                -- 6. Decimal
                -- 7. List
                """
                if( type == 4 ):
                    typeDescription = "DATE"
                    number_charac = None
                elif( type == 5 ):
                    typeDescription = "INT"
                elif( type == 6 ):
                    typeDescription = "DECIMAL"
                else:
                    typeDescription = "VARCHAR"

                if (required =='1'):
                    nullable = 'NOT NULL'
                else:
                    nullable = 'NULL'


                responseDataField = modelRawField.upsertColumnTable( model, "MODIFY COLUMN", name, typeDescription, number_charac, nullable )

                if( responseDataField.status == 'OK' ):
                    serializer.save()

                    return Response({'cid' : str(uuid.uuid4()),
                                    'status' : 'success',
                                    'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                                    'data' : [],}, status = status.HTTP_200_OK )

                else:
                    return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': responseDataField.msg,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

            return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': serializer.errors,
                            'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )

        return Response({'cid' : str(uuid.uuid4()),
                            'status' : 'error',
                            'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                            'data' : [],
                            'error': 'Not found',
                            'detailError' : [] }, status = status.HTTP_404_NOT_FOUND )

    def update( self,request,pk=None ): 
        field = self.get_serializer().Meta.model.objects.filter( id = pk ).first()
        if field:
            field.state = False
            field.save()
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
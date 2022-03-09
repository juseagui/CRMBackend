#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import connection

from apps.objects.api.serializers.object_serializers import ObjectSerializer,FieldSerializer, FieldCaptureSerializer
from apps.objects.models import Object, Field

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw
from apps.objects.mixins.validateField_mixins import validateField

#package bd django
from django.db.models import F
from django.db.models import Q
from datetime import datetime
import uuid



# -------------------------------------------------------------------------------------------------
# Manejo de viewset
# -------------------------------------------------------------------------------------------------

class ObjectViewSet( viewsets.ModelViewSet ):
    serializer_class = ObjectSerializer

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
        serializer = self.serializer_class( data = request.data, context={'request': '/objects'} )
        if serializer.is_valid():
            serializer.save()
            return Response( { 'message' : 'Se creo exitosamente el objeto', 'data' : serializer.data }  , status = status.HTTP_201_CREATED )
        return Response( serializer.errors , status = status.HTTP_400_BAD_REQUEST )

    def delete( self,request,pk=None ):
        product = self.get_queryset().filter(id = pk).first()
        if product:
            product.state = False
            product.save()
            return Response({'message':'Objeto Eliminado'},  status = status.HTTP_200_OK  )
        return Response({'error':'No existe un producto con estos datos'},  status = status.HTTP_400_BAD_REQUEST )
        

# -----------------------------------------------------------------------------------------------------
# Custom Field Get and Create 
# -- router : FieldObject
# -- params: visible 
#------------------------------------------------------------------------------------------------------

class FieldCoreCustomViewSet( viewsets.ModelViewSet ):
    serializer_class = FieldSerializer
    http_method_names = ['get','post','patch']
    parser_classes = (JSONParser,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):

        if(self.request.query_params.get('visible')):
            self.serializer_class = FieldSerializer
        elif(self.request.query_params.get('capture')):
            self.serializer_class = FieldCaptureSerializer
        else:
            return self.serializer_class

        return self.serializer_class
    
    def get_queryset( self, pk = None ):
        
        #define serializer work
        self.get_serializer_class()
        
        #filters query
        visible = self.request.query_params.get('visible')
        capture = self.request.query_params.get('capture')

        if( visible ):
            return self.get_serializer().Meta.model.objects.filter( 
                object_field = pk, 
                visible = visible,
                state = 1
            ).order_by('sort')

        elif(capture):
            action = self.request.query_params.get('action')

            if(action == 'edit'):
                return self.get_serializer().Meta.model.objects.filter( 
                    object_field = pk, 
                    state = 1,
                ).order_by('object_group__sort','sort')
            else:
                return self.get_serializer().Meta.model.objects.exclude(
               type_relation = 1
            ).filter(
                object_field = pk, 
                capture = capture,
                state = 1,
            ).order_by('object_group__sort','sort')
     

    def retrieve(self, request, pk=None):
        fieldObject = self.get_queryset( pk)
        # Query Get Fields of object
        dataReturn = self.get_serializer( fieldObject, many = True ).data

        capture = self.request.query_params.get('capture')
        action = self.request.query_params.get('action')
        pkModel = self.request.query_params.get('pk')

        if(capture and action == 'edit' and pkModel):
            data = list(dataReturn)
            #begin process action edit
            if data[0]:
                object = data[0].get('object_field')
                modelDefault = object.get('model')
                modelAlias = modelDefault+"_"+pk
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
                            join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = 1 "
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
                                                'code'        :  responseDataObject.data[0].get("code_"+itemFieldValue.get('name'))   }
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


            #final process action edit
            respAditional = {
            'created_date' : responseDataObject.data[0].get('created_date'),
            'modified_date' : responseDataObject.data[0].get('modified_date'),
            'data' : jsonData
            }
        
        else:
            respAditional = {
            'data' : dataReturn}

        return Response( {'cid' : str(uuid.uuid4()),
                         'status' : 'success',
                         'timestamp' : datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
                         'data' : respAditional }, status = status.HTTP_200_OK )

    def create(self, request):
        
        idObje = self.request.query_params.get('object')
        data = request.data
        #print(idObje, request.data)
        
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
        

# -----------------------------------------------------------------------------------------------------
#  Get data of object database
# -- router : getDataObject
#------------------------------------------------------------------------------------------------------

class DataObjectCustomViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        # Get data field for list datalist
        data = Field.objects.filter( 
            object_field = pk, visible = '1'
             ).values(
                'name','type','sort','visible', 'type_relation', 'object_list_id'
                ).annotate( 
                    model = F('object_field__model')).order_by('sort')

        # process data for get data in the object DB model
        if list(data)[0]:
            modelDefault = list(data)[0].get('model')
            modelAlias = modelDefault+"_"+pk
            nameField = ""
            join = ""
            countData = len(list(data))
            interator = 0

            #get field type relation = pk
            if (list(data)[0].get('type_relation') == 1 ):
                pk =  list(data)[0].get('name')
            
            for itemField in list(data):

                nameFieldBD = itemField.get('name')
                
                #validate relation for List
                if( itemField.get('type') == 7 and itemField.get('object_list_id') != None ):
                    nameField += "valuelist_"+nameFieldBD+".description "+nameFieldBD
                    join += " LEFT JOIN objects_valuelist valuelist_"+nameFieldBD+" "
                    join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = " + str(itemField.get('object_list_id'))
                else: 
                    nameField += modelAlias+"."+nameFieldBD

                interator += 1
                if(interator != countData):
                    nameField += ","

                
            
            #get params for pagination
            offset = self.request.query_params.get('offset') if self.request.query_params.get('offset') != None else 0
            limit = self.request.query_params.get('limit') if self.request.query_params.get('limit') != None else 15

            modelRawObject = ObjectModelRaw()

            #get count data of model
            responseCountDataObject = modelRawObject.getCountDataObject( modelDefault )

            #get data of model
            responseDataObject = modelRawObject.getDataObject( modelDefault, modelAlias, nameField, offset, limit, pk, None, None, join  )
 
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
                        'error': responseDataObject.msg ,
                        'detailError' : [] }, status = status.HTTP_400_BAD_REQUEST )


# -----------------------------------------------------------------------------------------------------
#  Get detail item in Object
# -- router : getDetailItemObject
#------------------------------------------------------------------------------------------------------

class DataDetailItemObjectViewSet( viewsets.ModelViewSet ):
    http_method_names = ['get']
    permission_classes = (IsAuthenticated,)

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
                    'object_group','required', 'columns', 'number_charac', 'object_list_id'
                    ).annotate( 
                        model = F('object_field__model'),
                        representation = F('object_field__representation'),
                        group_name = F('object_group__name')
                        ).order_by('object_group__sort','sort')
            
            # process data for get data in the object DB model
            if list(data)[0]:
                modelDefault = list(data)[0].get('model')
                modelAlias = modelDefault+"_"+pk
                representation = list(data)[0].get('representation')
                nameField = ""
                join = ""
                countData = len(list(data))
                interator = 0

                #get field type relation = pk
                if (list(data)[0].get('type_relation') == 1 ):
                    #validate ERROR when is null
                    pkName =  list(data)[0].get('name')
                

                for itemField in list(data):
                    nameFieldBD = itemField.get('name')
                
                    #validate relation for List
                    if( itemField.get('type') == 7 and itemField.get('object_list_id') != None ):
                        
                        print(itemField.get('object_list_id'))

                        nameField += "valuelist_"+nameFieldBD+".description "+nameFieldBD
                        nameField += ","+modelAlias+"."+nameFieldBD+" code_"+nameFieldBD
                        join += " LEFT JOIN objects_valuelist valuelist_"+nameFieldBD+" "
                        join += " ON valuelist_"+nameFieldBD+".code = "+modelAlias+"."+nameFieldBD+" AND valuelist_"+nameFieldBD+".list_id = "+ str(itemField.get('object_list_id'))
                    else: 
                        nameField += modelAlias+"."+nameFieldBD

                    interator += 1
                    if(interator != countData):
                        nameField += ","

                modelRawObject = ObjectModelRaw()
               
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
                        return Response( { 'created_date' : responseDataObject.data[0].get('created_date'),
                                        'modified_date' : responseDataObject.data[0].get('modified_date'),
                                        'data' : jsonData },  status = status.HTTP_200_OK )
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
        
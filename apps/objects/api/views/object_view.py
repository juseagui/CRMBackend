#package rest_framework
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

from apps.objects.api.serializers.object_serializers import ObjectSerializer,FieldSerializer, FieldCaptureSerializer
from apps.objects.models import Object, Field

#package personality querys bd and mixins
from apps.objects.mixins.models.object_model import ObjectModelRaw
from apps.objects.mixins.validateField_mixins import validateField

#package bd django
from django.db.models import F
from django.db.models import Q
import json



# -------------------------------------------------------------------------------------------------
# Manejo de viewset
# -------------------------------------------------------------------------------------------------

class ObjectViewSet( viewsets.ModelViewSet ):
    serializer_class = ObjectSerializer

    permission_classes = (IsAuthenticated,)
    
    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.filter( state = True ).order_by('order')

    def list( self, request):
        object_serializer = self.get_serializer( self.get_queryset(), many = True )
        return Response( object_serializer.data, status = status.HTTP_200_OK  )

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
        elif(self.request.query_params.get('detail')):
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
        detail = self.request.query_params.get('detail')

        if( visible ):
            return self.get_serializer().Meta.model.objects.filter( 
                                                                    object_field = pk, 
                                                                    visible = visible,
                                                                    state = 1
                                                                    ).order_by('order')
        elif(capture):
            #change serializers
            return self.get_serializer().Meta.model.objects.exclude(
                type_relation = 1
            ).filter( 
                object_field = pk, 
                capture = capture,
                state = 1,
            ).order_by('object_group__order','order')

        elif(detail):
            #change serializers
            return self.get_serializer().Meta.model.objects.exclude(
                type_relation = 1
            ).filter( 
                object_field = pk, 
                detail = detail,
                state = 1,
            ).order_by('object_group__order','order')

    def retrieve(self, request, pk=None):
        fieldObject = self.get_queryset( pk)
        # Query Get Fields of object
        object_serializer = self.get_serializer( fieldObject, many = True ).data
        return Response( object_serializer, status = status.HTTP_200_OK )

    def create(self, request):
        
        idObje = self.request.query_params.get('object')
        data = request.data
        #print(idObje, request.data)
        
        if(idObje != None):
            
            dataObject = Field.objects.filter( 
            object_field = idObje
             ).values(
                'name','type','order', 'type_relation', 'capture', 'required', 'number_charac'
                ).annotate( 
                    model = F('object_field__model')).order_by('order')
            
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
                        return Response({},  status = status.HTTP_201_CREATED )
                    else:
                        return Response({'error': 'error in query'  },  status = status.HTTP_400_BAD_REQUEST )    
                
                else:
                    return Response({'error': 'error in validate', 'detailError' : validateFieldData.getFieldError() },  
                                    status = status.HTTP_400_BAD_REQUEST )  

            else:
                return Response({'error': 'object not valid' },  status = status.HTTP_400_BAD_REQUEST )    
        else:
            return Response({'error': 'param object is required' },  status = status.HTTP_400_BAD_REQUEST )    

    def partial_update(self,  request, pk = None,):
        
        idObje = self.request.query_params.get('object')
        data = request.data

        if(idObje != None):
            
            dataObject = Field.objects.filter( 
            object_field = idObje
             ).values(
                'name','type','order', 'type_relation', 'capture', 'required', 'number_charac'
                ).annotate( 
                    model = F('object_field__model')).order_by('order')

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
                            return Response({},  status = status.HTTP_204_NO_CONTENT )
                        else:
                            return Response({'error': 'error in query'  },  status = status.HTTP_400_BAD_REQUEST )

                else:   
                        return Response({'error': 'error in validate', 'detailError' : validateFieldData.getFieldError() },  
                                        status = status.HTTP_400_BAD_REQUEST )

            else:
                 return Response({'error': 'object not valid' },  status = status.HTTP_400_BAD_REQUEST )    

        else:
            return Response({'error': 'param object is required' },  status = status.HTTP_400_BAD_REQUEST )   



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
                'name','type','order','visible', 'type_relation' 
                ).annotate( 
                    model = F('object_field__model')).order_by('order')

        # process data for get data in the object DB model
        if list(data)[0]:
            model = list(data)[0].get('model')
            nameField = ""
            countData = len(list(data))
            interator = 0

            #get field type relation = pk
            if (list(data)[0].get('type_relation') == 1 ):
                pk =  list(data)[0].get('name')
            

            for itemField in list(data):
                nameField += itemField.get('name')
                interator += 1
                if(interator != countData):
                    nameField += ","
            
            #get params for pagination
            offset = self.request.query_params.get('offset') if self.request.query_params.get('offset') != None else 0
            limit = self.request.query_params.get('limit') if self.request.query_params.get('limit') != None else 15

            modelRawObject = ObjectModelRaw()

            #get count data of model
            responseCountDataObject = modelRawObject.getCountDataObject( model )

            #get data of model
            responseDataObject = modelRawObject.getDataObject( model, nameField, offset, limit, pk, None )
 
            #validate Response
            if(responseDataObject.status == 'OK'):
                return Response( {'count' : responseCountDataObject.data[0]['count'],  'data' : responseDataObject.data} ,  status = status.HTTP_200_OK )
           
        return Response({'error': responseDataObject.msg },  status = status.HTTP_400_BAD_REQUEST )


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
                    'name','description', 'type','order','visible','detail', 'type_relation' , 'object_group','required', 'columns', 'number_charac'
                    ).annotate( 
                        model = F('object_field__model'),
                        representation = F('object_field__representation'),
                        group_name = F('object_group__name')
                        ).order_by('object_group__order','order')
            
            # process data for get data in the object DB model
            if list(data)[0]:
                model = list(data)[0].get('model')
                representation = list(data)[0].get('representation')
                nameField = ""
                countData = len(list(data))
                interator = 0

                #get field type relation = pk
                if (list(data)[0].get('type_relation') == 1 ):
                    #validate ERROR when is null
                    pkName =  list(data)[0].get('name')
                

                for itemField in list(data):
                    interator += 1
                    nameField += itemField.get('name')
                    if(interator != countData):
                        nameField += ","

                modelRawObject = ObjectModelRaw()
               
                #get data of model
                responseDataObject = modelRawObject.getDataObject( model, nameField, None, None, pkName, pk, representation )

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
           
            return Response({'error': responseDataObject.msg },  status = status.HTTP_400_BAD_REQUEST )
        
        return Response({'error': 'param object required' },  status = status.HTTP_400_BAD_REQUEST )
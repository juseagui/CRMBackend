from rest_framework import generics, viewsets
from apps.base.api import GeneralListApiView
from apps.objects.api.serializers.general_serializers import CategoryObjectSerializer, FieldobjectSerializer, GroupobjectSerializer


class CategoryObjectListAPIView( viewsets.ModelViewSet ):
    serializer_class = CategoryObjectSerializer

    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.filter( state = True )

class GroupObjectListAPIView( viewsets.ModelViewSet ):
    serializer_class = GroupobjectSerializer

    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.filter( state = True )

class FieldbjectListAPIView( viewsets.ModelViewSet ):
    serializer_class = FieldobjectSerializer
    
    def get_queryset( self, pk = None ):
        return self.get_serializer().Meta.model.objects.filter( state = True )



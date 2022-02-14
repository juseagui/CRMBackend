from rest_framework.routers import DefaultRouter
from apps.objects.api.views.object_view import ObjectViewSet, FieldCoreCustomViewSet, DataObjectCustomViewSet, DataDetailItemObjectViewSet
from apps.objects.api.views.general_view import *

router = DefaultRouter()


router.register(r'categoryObjects', CategoryObjectListAPIView , basename = 'CategoryObjects' )
router.register(r'groupObjects', GroupObjectListAPIView , basename = 'groupObjects' )
router.register(r'FieldObjects', FieldbjectListAPIView , basename = 'fieldObjects' )

# Get Objects
router.register(r'objects', ObjectViewSet , basename = 'objects' )

# Get data the fields the diferent objects
router.register(r'FieldObject', FieldCoreCustomViewSet , basename = 'objectsCustom' )

# Get data the objects of databases
router.register(r'getDataObject', DataObjectCustomViewSet , basename = 'objectsCustom' )

#Get Detail tiem in Object
router.register(r'getDetailItemObject',  DataDetailItemObjectViewSet , basename = 'objectsCustom' )


urlpatterns = router.urls 

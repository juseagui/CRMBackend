from rest_framework.routers import DefaultRouter
from apps.objects.api.views.object_view import ObjectViewSet, FieldCoreCustomViewSet, DataObjectCustomViewSet, DataDetailItemObjectViewSet
from apps.objects.api.views.permissions_view import objectsPermissionsCustomViewSet

router = DefaultRouter()


# Get Objects
router.register(r'objects', ObjectViewSet , basename = 'objects' )

# Get Permissions
router.register(r'objectsPermissions', objectsPermissionsCustomViewSet , basename = 'objectsPermissions' )

# Get, create and edit data the fields the diferent objects
router.register(r'FieldObject', FieldCoreCustomViewSet , basename = 'objectsCustom' )

# Get data the objects of databases
router.register(r'getDataObject', DataObjectCustomViewSet , basename = 'objectsCustom' )

#Get Detail tiem in Object
router.register(r'getDetailItemObject',  DataDetailItemObjectViewSet , basename = 'objectsCustom' )


urlpatterns = router.urls 

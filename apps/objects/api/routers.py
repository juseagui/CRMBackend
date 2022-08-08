from rest_framework.routers import DefaultRouter

#import app objects
from apps.objects.api.views.object_view import ObjectViewSet ,RelationshipViewSet
from apps.objects.api.views.data_view import DataObjectCustomViewSet
from apps.objects.api.views.field_view import FieldViewSet
from apps.objects.api.views.permissions_view import objectsPermissionsCustomViewSet

#import app processes
from apps.processes.api.views.processes_view import ProcessViewSet

router = DefaultRouter()

# Get Objects
router.register(r'objects', ObjectViewSet , basename = 'Objects' )

# Relationship object
router.register(r'relations', RelationshipViewSet , basename = 'Relationsobjects' )

# Get Permissions
router.register(r'permissions', objectsPermissionsCustomViewSet , basename = 'objectsPermissions' )

# Get, create and edit data the fields the diferent objects
router.register(r'field', FieldViewSet , basename = 'objectsCustom' )

# Get data the objects of databases
router.register(r'data', DataObjectCustomViewSet , basename = 'objectsCustom' )

# Get data processes
router.register(r'procesess', ProcessViewSet , basename = 'Procesess' )

urlpatterns = router.urls 

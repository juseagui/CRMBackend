from rest_framework.routers import DefaultRouter

#import app objects
from apps.objects.api.views.object_view import ObjectViewSet ,RelationshipViewSet
from apps.objects.api.views.data_view import DataObjectCustomViewSet
from apps.objects.api.views.field_view import FieldViewSet
from apps.objects.api.views.permissions_view import objectsPermissionsCustomViewSet

#import app processes
from apps.processes.api.views.processes_view import ProcessViewSet
from apps.processes.api.views.historical_view import HistoricalViewSet

#import app reports
from apps.reports.api.views.reports_view import ReportsProcessViewSet, ReportsProgramViewSet

#import app user
from apps.users.views import UserAccessViewSet

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


# Get and created flow data processes
router.register(r'procesess', ProcessViewSet , basename = 'Procesess' )

# Get and created flow data processes
router.register(r'historical', HistoricalViewSet , basename = 'HistoricalProcesess' )

# Get reports data
router.register(r'reports/process', ReportsProcessViewSet , basename = 'ReportsProcess' )
router.register(r'reports/program', ReportsProgramViewSet , basename = 'ReportsProgram' )

# Change password
router.register(r'user/changepassword', UserAccessViewSet , basename = 'ChangePassword' )


urlpatterns = router.urls 

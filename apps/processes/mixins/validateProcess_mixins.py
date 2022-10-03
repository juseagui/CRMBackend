from apps.processes.models import Activity, HistoricalProcess

#package bd django
from django.db.models import F
from django.utils import timezone

class validateProcess:
    def __init__( self, object, user, process, pk = None, **kwargs ):
        #id object
        self.object = object
        self.pkData = pk
        self.dataActivities = []
        self.process = process,
        self.user = user

    
    def validateExistProcessObject( self ):

        #get data process
        self.dataActivities = Activity.objects.filter(
            process_activity__object_process = self.object
            ).values(
            'id','description','process_activity','code','process_state','sort'
            ).order_by('sort')

        #get process id
        if self.dataActivities:
            self.process = self.dataActivities[0]['process_activity']

        return self.dataActivities

    def validateExistHistoricalProcess( self, lastRecord = False ):

        if(self.pkData):
            #get historical process for pk
            self.dataHistorical = HistoricalProcess.objects.filter(
                object_historical__id = self.object,
                process_historical__id = self.process,
                id_record = self.pkData
                ).values(
                    'description',
                    'start_date','finish_date',
                    'object_historical','process_historical','activity_historical',
                    'user_historical', 
                    user_name=F('user_historical__name'), 
                    user_lastname=F('user_historical__last_name'),
                    user_email=F('user_historical__email')
                ).order_by('-start_date')
        
        else :
                #get historical process
                self.dataHistorical = HistoricalProcess.objects.filter(
                    object_historical__id = self.object,
                    process_historical__id = self.process,
                    ).values(
                        'description',
                        'start_date','finish_date',
                        'object_historical','process_historical','activity_historical',
                        'user_historical', 
                        user_name=F('user_historical__name'), 
                        user_lastname=F('user_historical__last_name'),
                        user_email=F('user_historical__email')
                    ).order_by('-start_date')
            
        if ( lastRecord ):
            self.dataHistorical = self.dataHistorical[:1]

        return self.dataHistorical


    def endOldActivities( self, idRecord ):
        self.dataHistorical = HistoricalProcess.objects.filter(
                    object_historical__id = self.object,
                    process_historical__id = self.process[0],
                    id_record = idRecord,
                    finish_date__isnull = True
                    ).update( finish_date = timezone.now() )
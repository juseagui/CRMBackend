from django.db import models
from apps.base.models import BaseModel
from apps.objects.models import Object
from apps.users.models import User

class Process(BaseModel):
    description = models.CharField('Description', max_length=50,blank = False,null = False,unique = False)
    object_process = models.ForeignKey(Object, on_delete=models.CASCADE,related_name= 'object_process', verbose_name = 'object_process')

    class Meta:
        """Meta definition for process."""
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'

    def __str__(self):
        """Unicode representation of process."""
        return self.description


class Activity(BaseModel):
    description = models.CharField('Description', max_length=50,blank = False,null = False,unique = False)
    process_activity = models.ForeignKey(Process, on_delete=models.CASCADE, related_name= 'processActivity', verbose_name = 'ProcessActivity')
    code = models.CharField('Code of Activity', max_length=50, unique = False,blank = False,null = False)
    process_state = models.CharField('State of Activity', max_length=11, unique = False,blank = False,null = False)
    sort = models.IntegerField('Order of Activity',  blank = False,null = False)

    class Meta:
        """Meta definition for process."""
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'
        constraints = [
            models.UniqueConstraint(fields=['code', 'process_activity'], name='unique_processActivty')
        ]
        ordering = ['sort']

    def __str__(self):
        """Unicode representation of process."""
        return self.description


class HistoricalProcess(BaseModel):
    description = models.CharField('Description', max_length=2000,blank = False,null = False,unique = False)
    id_record = models.IntegerField('record id ',  blank = False,null = False)
    object_historical = models.ForeignKey(Object, on_delete=models.CASCADE,related_name= 'object_historical', verbose_name = 'object_historical')
    process_historical = models.ForeignKey(Process, on_delete=models.CASCADE,related_name= 'process_historical', verbose_name = 'process_historical')
    activity_historical = models.ForeignKey(Activity, on_delete=models.CASCADE,related_name= 'activity_historical', verbose_name = 'activity_historical')
    user_historical = models.ForeignKey(User, on_delete=models.CASCADE,related_name= 'user_historical', verbose_name = 'user_historical')
    start_date = models.DateTimeField('Start date', auto_now=False, auto_now_add=True)
    finish_date = models.DateTimeField('Finish date', blank = True,null = True, auto_now=False, auto_now_add=False)

    class Meta:
        """Meta definition for process."""
        verbose_name = 'Historical Process'
        verbose_name_plural = 'Historical Processes'

    def __str__(self):
        """Unicode representation of Historical."""
        return self.description
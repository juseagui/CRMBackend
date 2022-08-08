from django.db import models
from apps.base.models import BaseModel
from apps.objects.models import Object

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
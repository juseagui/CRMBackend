from django.contrib import admin
from apps.objects.models import *

# Register your models here.
class CategoryObjectAdmin( admin.ModelAdmin ):
    #Controlar la visualizacion en el despliegue de administracion django
    list_display = ('id','description')

admin.site.register(CategoryObject)
admin.site.register(Object)
admin.site.register(Group)
admin.site.register(Field)
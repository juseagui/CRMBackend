from django.db import models
from apps.base.models import BaseModel


class CategoryObject(BaseModel):
    name = models.CharField('Name', max_length=25,blank = False,null = False,unique = True)
    description = models.CharField('Description', max_length=50,blank = False,null = False,unique = False)
    icon = models.CharField('Icon', max_length=50, blank = True,null = True)

    class Meta:
        """Meta definition for MeasureUnit."""

        verbose_name = 'Categoria de Objeto'
        verbose_name_plural = 'Categorias de Objetos'

    def __str__(self):
        """Unicode representation of MeasureUnit."""
        return self.description

# Create your models here.
class Object(BaseModel):
    name = models.CharField('Object name', max_length=150, unique = True,blank = False,null = False)
    description = models.TextField('Object Description',blank = False,null = False)
    icon = models.CharField('Icon', max_length=50, blank = True,null = True)
    category_object = models.ForeignKey(CategoryObject, on_delete=models.CASCADE, verbose_name = 'category_object', related_name= 'category_object')
    view = models.CharField('View', max_length=150, blank = True,null = True)
    sort = models.IntegerField('Sort',  blank = True,null = True)
    model = models.CharField('Model Database', max_length=150, unique = False,blank = False,null = False)

    #ubication in system
    visible = models.CharField('Visible', max_length=50, blank = True,null = True)

    #Field Configuration __str__
    representation = models.CharField('Representation Object', max_length=150, unique = False,blank = True,null = True)

    class Meta:
        """Meta definition for Product."""
        verbose_name = 'Object'
        verbose_name_plural = 'Objects'

    def __str__(self):
        """Unicode representation of Objects."""
        return self.name


# Create your models here.
class Group(BaseModel):

    name = models.CharField('Nombre del grupo', max_length=150, unique = True,blank = False,null = False)
    object_group = models.ForeignKey(Object, on_delete=models.CASCADE, verbose_name = 'Objeto')
    sort = models.IntegerField('Sort',  blank = True,null = True)

    class Meta:
        """Meta definition for Group."""

        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        """Unicode representation of Group."""
        return self.name

# Create your models here.
class List(BaseModel):

    name = models.CharField('Nombre de la lista', max_length=150, unique = True,blank = False,null = False)
    native = models.BooleanField('Is native App',default = False)

    class Meta:
        """Meta definition for Lists."""

        verbose_name = 'List'
        verbose_name_plural = 'Lists'

    def __str__(self):
        """Unicode representation of Lists."""
        return self.name
    

# Create your models here.
class Field(BaseModel):

    name = models.CharField('Field in BD', max_length=150, unique = False,blank = False,null = False)
    description = models.CharField('Description Field', max_length=150, unique = False,blank = False,null = False)
    hint = models.CharField('Hint Field', max_length=200, unique = False,blank = True,null = True)
    type = models.IntegerField('Type',  blank = False,null = False)
    type_relation = models.IntegerField('TypeRelation',  blank = True,null = True)
    sort = models.IntegerField('Sort',  blank = True,null = True)

    #---------------------------------------------------------------------------------
    # Relation table FK
    #---------------------------------------------------------------------------------
    object_field = models.ForeignKey(Object, on_delete=models.CASCADE,related_name= 'fields' , verbose_name = 'Object')
    object_group = models.ForeignKey(Group, on_delete=models.CASCADE,related_name= 'group_field',  verbose_name = 'Group')
    object_list = models.ForeignKey(List, on_delete=models.CASCADE,related_name= 'lists',  verbose_name = 'List', blank = True,null = True)

    
    #initial information display
    visible = models.CharField('Visible', max_length=50, blank = False,null = False)
    #information display in form of capture data
    capture = models.CharField('Capture', max_length=50, blank = False,null = False)
    #information display in detail
    detail = models.CharField('Detail', max_length=50, blank = False,null = False)
    
    #---------------------------------------------------------------------------------
    #props field
    #---------------------------------------------------------------------------------
    required = models.CharField('Required',max_length=50, blank = False,null = False )
    number_charac = models.IntegerField('Number of characters', blank = True,null = True )
    columns = models.IntegerField('Position in form for columns', blank = True,null = True )
    
    
    class Meta:
        """Meta definition for Field."""

        verbose_name = 'Field'
        verbose_name_plural = 'Fields'
        ordering = ['sort']

    def __str__(self):
        """Unicode representation of Field."""
        return self.name


# Create your models here.
class ValueList(BaseModel):

    description = models.CharField('Description Value of List', max_length=150, unique = False,blank = False,null = False)
    code = models.CharField('Code Value of List', max_length=50, unique = False,blank = False,null = False)
    sort = models.IntegerField('Order Value')
    list = models.ForeignKey(List, on_delete=models.CASCADE,related_name= 'ListValues',  verbose_name = 'ListValues', )

    class Meta:
        """Meta definition for ValueList."""
        verbose_name = 'Value of List'
        verbose_name_plural = 'Values of List'
        constraints = [
            models.UniqueConstraint(fields=['code', 'list'], name='unique ValueList')
        ]
        ordering = ['sort']

    def __str__(self):
        """Unicode representation of ValueList."""
        return self.description



# ------------------------------------------------------------
#-------- MODEL PERMISSIONS
#-------------------------------------------------------------

class Rol(BaseModel):
    description = models.CharField('Description Rol', max_length=150, unique = False,blank = False,null = False)

    class Meta:
        """Meta definition for Rol."""
        verbose_name = 'Rol'
        verbose_name_plural = 'Rols'
    def __str__(self):
        """Unicode representation of Rol."""
        return self.description

class Permission(BaseModel):
    
    #relation object and rol
    object_permission = models.ForeignKey(Object, on_delete=models.CASCADE,related_name= 'object_rol' , verbose_name = 'object_rol')
    rol_permission = models.ForeignKey(Rol, on_delete=models.CASCADE,related_name= 'rol_permission' , verbose_name = 'rol_permission')

    #detail of permissions
    visible = models.CharField('Visible', max_length=50, blank = True,null = True)
    add_data = models.CharField('Add Data', max_length=50, blank = True,null = True)
    edit_data = models.CharField('Edit Data', max_length=50, blank = True,null = True)
    delete_data = models.CharField('Delete Data', max_length=50, blank = True,null = True)

    constraints = [
            models.UniqueConstraint(fields=['object_permission', 'rol_permission'], name='unique rol_permission')
        ]

    class Meta:
        """Meta definition for rol_permission."""
        verbose_name = 'Rol permission'
        verbose_name_plural = 'Rols permission'
    def __str__(self):
        """Unicode representation of Rol."""
        return self.description

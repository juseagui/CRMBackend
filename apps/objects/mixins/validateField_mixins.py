import datetime

class validateField:
    def __init__(self,  object, propertyField, **kwargs):
        #data object
        self.object = object
        #data type queryset of property field
        self.propertyField = propertyField

        # ----------------------------------
        self.model = ""
        self.fieldError = []
        self.stringInsert = ""
        self.stringValues = ""
        self.stringUpdate = ""
        # ---------------------------------
        self.pkName = ""
    
    # getter function and setter function
    def getFieldError(self):
        # Do something if you want
        return self.fieldError

    def getStringInsert(self):
        # Do something if you want
        return self.stringInsert

    def getStringValues(self):
        # Do something if you want
        return self.stringValues

    def getStringUpdate(self):
        # Do something if you want
        return self.stringUpdate
    
    def getPkName(self):
        # Do something if you want
        return self.pkName
    
    def getModel(self):
        # Do something if you want
        return self.model


    def validateListField(self,data,**kwargs):
        
        existPrimaryKey = False

        for itemFieldProperty in list(self.propertyField):
            if(itemFieldProperty.get('type_relation') != 1):

                #set model
                if(self.model == ""):
                    self.model = itemFieldProperty.get('model')

                try:
                    value = data[itemFieldProperty.get('name')]
                except:
                    value = ""

                valid = self.validateFieldType( itemFieldProperty,value )

                if(valid):
                    self.generateQueryTransation( itemFieldProperty, value )
            else:
                existPrimaryKey = True
                self.pkName = itemFieldProperty.get('name')

        if(not existPrimaryKey):
            msg = "Primary key is not parameterized"
            self.fieldError.append({ self.object : {
                'error' : True,
                'msg'   : msg
            }  })

        self.refactorQueryInsert()
        self.refactorQueryupdate()

    
    
    def validateFieldType(self, fieldProperty, value, **kwargs):
        
        if(value == None ):
            value = ""

        if( fieldProperty.get('required') == '1' ):
            if(value == ""):
                msg = "Field is required || not empty"
                self.fieldError.append({ fieldProperty.get('name') : {
                    'error' : True,
                    'msg'   : msg
                }  })
                return False

        #validate type num
        if( fieldProperty.get('type') == 5 ):
            try:
                int( value if value else  0)
            except:
                msg = "Field only Number"
                self.fieldError.append({ fieldProperty.get('name') : {
                    'error' : True,
                    'msg'   : msg
                }  })
                return False

        #Validate Date
        elif( fieldProperty.get('type') == 4  ):
            try:
                datetime.datetime.strptime(value, '%Y-%m-%d')
            except :
                msg = "Incorrect data format, should be YYYY-MM-DD"
                self.fieldError.append({ fieldProperty.get('name') : {
                    'error' : True,
                    'msg'   : msg
                }  })
                return False

        #Validate String        
        if( len(str(value)) > fieldProperty.get('number_charac') ):
            msg = "the length of the text exceeds that of the field - allowed length : "+str(fieldProperty.get('number_charac'))
            self.fieldError.append({ fieldProperty.get('name') : {
                'error' : True,
                'msg'   : msg
            }  })
            return False
        
        return True


    def generateQueryTransation(self, fieldProperty, value, **kwargs):

        self.stringInsert += fieldProperty.get('name')+","

        #validate type num
        if(value == "" or value == None):
            self.stringValues += "NULL,"
            self.stringUpdate += fieldProperty.get('name')+" = NULL,"
            return

        if( fieldProperty.get('type') != 5 ):
            self.stringValues += "'"+value+"',"
            self.stringUpdate += fieldProperty.get('name')+" = "+"'"+value+"',"
        else:
            self.stringValues += str(value)+","
            self.stringUpdate += fieldProperty.get('name')+" = "+str(value)+","


    def refactorQueryInsert(self):
        self.stringInsert += "created_date, modified_date, deleted_date, state"
        self.stringValues += "NOW(), NOW(), NOW(), 1"
    
    def refactorQueryupdate(self):
        self.stringUpdate += "modified_date = NOW()"

       
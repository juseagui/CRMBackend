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

                nameExist = data[itemFieldProperty.get('name')]
                value = nameExist
                valid = self.validateFieldType( itemFieldProperty,value )

                if(valid):
                    self.generateQueryTransation( itemFieldProperty, value )
            else:
                existPrimaryKey = True

        if(not existPrimaryKey):
            msg = "Primary key is not parameterized"
            self.fieldError.append({ self.object : {
                'error' : True,
                'msg'   : msg
            }  })

        self.refactorQueryInsert()
        #self.refactorQueryUpdate()

    
    
    def validateFieldType(self, fieldProperty, value, **kwargs):
        
        #print(fieldProperty ,value )

        if( fieldProperty.get('required') == '1' ):
            print(fieldProperty.get('name'), value)
            if(value == "" or value == None ):
                msg = "Field is required || not empty"
                self.fieldError.append({ fieldProperty.get('name') : {
                    'error' : True,
                    'msg'   : msg
                }  })
                return False

        #validate type num
        if( fieldProperty.get('type') == 5 ):
            try:
                int(value)
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
        
        
        return True


    def generateQueryTransation(self, fieldProperty, value, **kwargs):

        self.stringInsert += fieldProperty.get('name')+","

        #validate type num
        if(value == "" or value == None):
            self.stringValues += "NULL"
            return

        if( fieldProperty.get('type') != 5 ):
            self.stringValues += "'"+value+"',"
        else:
            self.stringValues += value+","


    def refactorQueryInsert(self):
        self.stringInsert += "created_date, modified_date, deleted_date"
        self.stringValues += "NOW(), NOW(), NOW()"
        

       
class generatedQuery:
      
      def generateWhereFilter( self, data, nameField, modelAlias, **kwargs ):
        
        whereFilter = ""
        
        for itemFilterField in list(data):
            if( itemFilterField.get('name') == nameField):
                if( itemFilterField.get('filter').get('operation') and itemFilterField.get('filter').get('value') ):
                    operation = ""
                    aditionalChar = ""
                    if( itemFilterField.get('filter').get('operation') == 'equal' ):
                        operation = "="
                    elif( itemFilterField.get('filter').get('operation') == 'different' ):  
                        operation = "!="
                    elif( itemFilterField.get('filter').get('operation') == 'contain' ):
                        operation =  "LIKE"
                        aditionalChar = "%"
                
                    whereFilter += modelAlias+"."+nameField + " " + operation
                    whereFilter +=  " '"+aditionalChar+itemFilterField.get('filter').get('value')+aditionalChar+"' "
            
        return whereFilter
                    


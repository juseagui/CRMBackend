from django.db import connection
from collections import namedtuple


""" 
Class for response standar in model RAW Query
in the view
""" 
class ResponseDataQuery(object):
    def __init__(self, status, msg = "", data = []):
        self.status = status
        self.msg = msg
        self.data = data


"""
    Alter table -- add field
"""

class FieldModelRaw(object):

    def upsertColumnTable(self, model, operation, name, typeDescription, number_charac, nullable ):
        with connection.cursor() as cursor:
            try:
                  
                query  = "ALTER TABLE "+model+" "
                query +=  operation+" "+name+" "

                if( number_charac != None ):
                    query += typeDescription+"("+str(number_charac)+") "
                else:
                    query += typeDescription+" "
                
                query += nullable
                
                cursor.execute( query )
                responseReturn = ResponseDataQuery('OK','',None)
            except Exception as err:
                msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()

        return responseReturn
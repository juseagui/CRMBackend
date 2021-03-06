from django.db import connection
from collections import namedtuple

""" 
Class for response standar in model RAW Query
in the view
""" 
class ResponseDataQuery(object):
    def __init__(self, status, msg, data):
        self.status = status
        self.msg = msg
        self.data = data


""" 
custom queries to tables that 
don't exist in django model
""" 

class ObjectModelRaw(object):

    """
    return format tuple
    """
    def namedtuplefetchall(self, cursor):
        "Return all rows from a cursor as a namedtuple"
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]

    """
    return format dictionary
    In use
    """
    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0]
        for col in cursor.description ]
        return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]

    """
    get information dynamically from a specific table
    """
    def getDataObject(self, model, fields, offset = 0, limit = 15, pkName = None, pk = None, representation = None ):
        with connection.cursor() as cursor:
            try:
                query = "SELECT "+pkName+" AS pk ,"+fields+" , created_date, modified_date  "
                
                if representation:
                    query += ","+representation+" AS representation" 

                query += " FROM "+model+" "

                if(offset and limit):
                    query += "LIMIT "+offset+","+limit+" "

                if(pk):
                    query += "WHERE "+pkName+" = "+pk


                cursor.execute( query )
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn

    """
    get count item in the model DB
    """
    def getCountDataObject(self, model ):
        with connection.cursor() as cursor:
            try:
                query = "SELECT COUNT(1) count FROM "+model+" "
                cursor.execute( query )
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn



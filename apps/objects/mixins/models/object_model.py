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
    def getDataObject(self, model, modelAlias, fields, offset = 0, limit = 15, pkName = None, pk = None, representation = None, join = "", conditional = None ):
        with connection.cursor() as cursor:
            try:
                query = "SELECT "+modelAlias+"."+pkName+" AS pk ,"+fields+" , "+modelAlias+".created_date, "+modelAlias+".modified_date  "
                
                if representation:
                    query += ","+representation+" AS representation_core " 

                query += " FROM "+model+" "+modelAlias+" "

                if(join):
                    query += join

                if(pk or conditional ):
                    query += " WHERE "
                    aditionalQuery = ""
                    if(pk):
                        query += " "+modelAlias+"."+pkName+" = "+pk
                        aditionalQuery += " AND "
                    if(conditional):
                        query += aditionalQuery+conditional

                if(offset and limit):
                    query += " LIMIT "+offset+","+limit+" "
                
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
    def getCountDataObject(self, model, conditional = None ):
        with connection.cursor() as cursor:
            try:
                query = "SELECT COUNT(1) count FROM "+model+" "

                if( conditional ):
                    query += " WHERE "+ conditional

                cursor.execute( query )
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn

    """
    insert information dynamically from a specific table
    """
    def postDataObject(self, model, fields, values):
        with connection.cursor() as cursor:
            try:
                query = "INSERT INTO "+model+" ("+fields+")"
                query += "VALUES ("+values+")"
                print(query)
                cursor.execute( query )
                results = []
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn


    """
    update partial information dynamically from a specific table
    """
    def updateDataObject (self, model, fields, pkName, pk):
        with connection.cursor() as cursor:
            try:
                query = "UPDATE "+model+" SET "
                query += fields+" WHERE  "+pkName+" = "+pk
                print(query)
                cursor.execute( query )
                results = []
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn


    """
    get table in system
    """
    def getTableSystem(self, model ):
        with connection.cursor() as cursor:
            try:
                query  = "SELECT TABLE_NAME FROM information_schema.tables "
                query += "WHERE  TABLE_NAME = '"+model+"' "
                cursor.execute( query )
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn

    
    """
    create table in system
    """
    def postTableSystem(self, model ):
        with connection.cursor() as cursor:
            try:
                query  = "CREATE TABLE IF NOT EXISTS "+model+" ( "
                query += " id INT AUTO_INCREMENT PRIMARY KEY, "
                query += " state tinyint(1), "
                query += " created_date date, "
                query += " modified_date date, "
                query += " deleted_date date "
                query += " ) "
                
                cursor.execute( query )
                results = []
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn
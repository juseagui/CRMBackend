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

class ReportModelRaw(object):

    """
    return format tuple
    """
    def namedtuplefetchall(self, cursor):
        "Return all rows from a cursor as a namedtuple"
        desc = cursor.description
        nt_result = namedtuple('Result', [col[0] for col in desc])
        return [nt_result(*row) for row in cursor.fetchall()]

    """
    return format dictionary (In use)
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
    Obtain information on the number of leads per process
    """
    def getStateProcess( self ):
        with connection.cursor() as cursor:
            try:
                query  = "SELECT  COUNT(1) count_act ,ACT.process_state process_state "
                query += "FROM opportunities OP "
                query += "INNER JOIN  processes_historicalprocess HOP "
                query += "ON  OP.id = HOP.id_record AND IFNULL(HOP.finish_date, '0') = '0'"
                query += "LEFT JOIN processes_activity ACT "
                query += "ON HOP.activity_historical_id = ACT.id "
                query += "WHERE OP.state = '1' "
                query += "GROUP BY ACT.process_state "
                print(query)
                cursor.execute( query )
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn

    
    """
    Obtain value information by process status
    """
    def getStateValueProcess(self ):
        with connection.cursor() as cursor:
            try:
                query  = "SELECT  COUNT(1) count_act ,ACT.process_state process_state, SUM(pro.value) value_total "
                query += "FROM opportunities OP "
                query += "INNER JOIN  processes_historicalprocess HOP "
                query += "ON  OP.id = HOP.id_record AND IFNULL(HOP.finish_date, '0') = '0'"
                query += "LEFT JOIN processes_activity ACT "
                query += "ON HOP.activity_historical_id = ACT.id "
                query += "INNER JOIN `program` PRO "
                query += "ON PRO.id = OP.program_id "
                query += "WHERE OP.state = '1' "
                query += "GROUP BY ACT.process_state "
                cursor.execute( query )
                print(query)
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn

    """
    get number of opportunities by date
    """
    def getStateCountProcess(self ):
        with connection.cursor() as cursor:
            try:
                query  = "SET lc_time_names = 'es_MX' "
                cursor.execute( query )
                query = "SELECT  DATE_FORMAT(created_date, \"%M\") as period, COUNT(1)AS count_opportunity "
                query += "FROM opportunities  "
                query += "GROUP BY DATE_FORMAT(created_date, \"%m\") "
                query += "ORDER BY  MONTH(created_date) DESC "
                cursor.execute( query )
                print(query)
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn
    

    """
    Obtain value information by process status
    """
    def getStateProgram(self ):
        with connection.cursor() as cursor:
            try:
                query  = "SELECT  PRO.description AS description_program , PRO.id AS id_program, COUNT(1) count_program, SUM(pro.value) value_total "
                query += "FROM opportunities OP "
                query += "INNER JOIN `program` PRO ON PRO.id = OP.program_id "
                query += "INNER JOIN  processes_historicalprocess HOP  "
                query += "ON  OP.id = HOP.id_record AND IFNULL(HOP.finish_date, '0') = '0' "
                query += "LEFT JOIN processes_activity ACT "
                query += "ON HOP.activity_historical_id = ACT.id "
                query += "WHERE OP.state = '1' AND ACT.process_state <> 4 "
                query += "GROUP BY PRO.id "
                cursor.execute( query )
                print(query)
                results = self.dictfetchall(cursor)
                responseReturn = ResponseDataQuery('OK','',results)
            except Exception as err:
                  msg = 'Failure in executing query {0}. Error: {1}'.format(query, err)
                  responseReturn = ResponseDataQuery('ERROR',msg, None)
            
            cursor.close()
        return responseReturn
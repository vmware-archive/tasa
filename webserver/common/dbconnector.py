# -*- coding: utf-8 -*-
'''
  Srivatsan Ramanujam <sramanujam@gopivotal.com>
  DBConnector class to manage all things involved in connecting to the Greenplum database, fetching records etc.
'''

import psycopg2
from psycopg2 import extras
from psycopg2 import pool
from contextlib import contextmanager
import time, sys
import os
import json

class DBConnect(object):
        @classmethod
        def getConnectionString(cls):
            ''' 
                Read the DB connection parameters from a config file.
                You should create a file in your home directory : ~/.dbconn.config 
                that should look like so :
                ------------------
                [db_connection]
                user = gpadmin
                password = XXXXX
                hostname = 127.0.0.1 (or the IP of your DB server)
                port = 5432 (the port# of your DB)
                database = vatsandb (the database you wish to connect to)
                ------------------
                Output : Returns the connection string of the form :
                "host='{hostname}' port ='{port}' dbname='{database}' user='{username}' password='{password}'"
            '''
            import os
            import ConfigParser
            config_file = os.path.join(os.path.expanduser('~'),'.dbconn.config')
          
            config = ConfigParser.ConfigParser()
            if( not os.path.exists(config_file)):
                raise Exception('DB connection configuration file not found at {path}'.format(path=config_file))
              
            config.read(config_file)
            username = config.get('db_connection','user')
            password = config.get('db_connection','password')
            hostname = config.get('db_connection','hostname')
            port = config.get('db_connection','port')
            database = config.get('db_connection','database')
            conn_string = "host='{hostname}' port ='{port}' dbname='{database}' user='{username}' password='{password}'"
            conn_string = conn_string.format(hostname=hostname,port=port,database=database,username=username,password=password)
            conn_dict = {}
            conn_dict['username']=username
            conn_dict['password']=password
            conn_dict['hostname']=hostname
            conn_dict['port']=port
            conn_dict['database']=database
            conn_dict['conn_string']=conn_string
        
            return conn_dict    
 
        def __initConnectionPool__(self, conn_str):
            '''Initialize a Connection Pool'''
            self.pool = psycopg2.pool.SimpleConnectionPool(1,10, conn_str if conn_str else DBConnect.getConnectionString()['conn_string'])          

       
        def __init__(self,conn_str=None):
            ''' Connect to the DB using Psycopg2, if conn_str is not provided, read it from VCAP_SERVICES '''
            if(not conn_str):
                vcap_services = json.loads(os.environ['VCAP_SERVICES'])
                creds = vcap_services['user-provided'][0]['credentials']
                conn_str = "host='{hostname}' port ='{port}' dbname='{database}' user='{username}' password='{password}'"
                conn_str = conn_str.format(
                              hostname=creds['hostname'],
                              port=creds['port'],
                              database=creds['databasename'],
                              username=creds['username'],
                              password=creds['password']
                           )
            self.conn_str = conn_str
            self.__initConnectionPool__(conn_str)

 
        def __is_dbconn_alive__(self):
            '''Ping the DB and check if the connection is alive - It seems like conn.closed doesn't work all the time '''
            ping_cmd = '''select 1;'''
            conn_alive = True
            isQuery = True
            with self.getCursor(isQuery) as cursor:
                try:
                    cursor.execute(ping_cmd)
                except psycopg2.Error, e:
                    print 'Error: ',e
                    conn_alive = False
            return conn_alive

        def __reconnect_if_closed__(self,conn_str=None):
            '''
               Reconnect if the connection has failed/timed-out or has been closed down
            '''
            if(self.pool.closed or not self.__is_dbconn_alive__()):
                self.pool.closeall()
                print '*** Detected closed connections. Reconnecting...'
                self.__initConnectionPool__(self.conn_str)
                
        @contextmanager    
        def getCursor(self,isQuery, withhold=False):
            ''' Return a named cursor. You don't have to close named cursor ''' 
            cursor_name = str(time.time()) 
            conn = self.pool.getconn()
            executionStatus = ''
            try:
                cursor = conn.cursor(cursor_name,cursor_factory=extras.DictCursor,withhold=withhold) if isQuery else conn.cursor()
                yield cursor
            except Exception, e:
                executionStatus = e.pgerror
                _exType, _exVal, exTrace = sys.exc_info()
                print 'Execution Status:',executionStatus
                print 'Stacktrace :',dir(exTrace)
                print 'Query: ',cursor.query
            finally:
                if(executionStatus != ''):
                     conn.rollback()
                else:
                     conn.commit()
                self.pool.putconn(conn)
        
        def executeQuery(self,query):
            ''' 
                Execute a Query
                Inputs:
                =======
                      query - (string) the query to be executed
                Outputs:
                ========
                      executionStatus - (string) Errors if any 
            '''
            self.__reconnect_if_closed__()
            executionStatus = 'FAILED'
            isQuery=False
            with self.getCursor(isQuery) as cursor:
                 cursor.execute(query)
                 executionStatus = ''

            return executionStatus
                
        def fetchRows(self, query):
            '''
               Return a list of all rows fetched from the cursor.
               WARNING :
               ========= 
               Calling this method is discouraged if the query returns a large number of rows.
               It is recommended that you iterate over the cursor in that case.
               
               Inputs:
               =======
               query : (string) the select query to execute
        
               Outputs:
               ========
               A list of all rows fetched from the cursor
            '''
            self.__reconnect_if_closed__()
            rows=[]
            executionStatus = 'FAILED'
            isQuery = True
            with self.getCursor(isQuery) as cursor:
                 cursor.execute(query)
                 executionStatus = ''
                 rows.extend([r for r in cursor])

            return executionStatus,rows

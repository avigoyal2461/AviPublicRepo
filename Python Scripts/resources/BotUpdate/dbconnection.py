import pandas as pd
import pyodbc
import os
import time
import json
import struct
from datetime import datetime, timedelta, timezone
#CONFIG_PATH = os.path.dirname(os.path.abspath(__file__))
#CONFIG_PATH = '\\'.join([CONFIG_PATH, 'config.json'])
import os
import sys
sys.path.append(os.environ['autobot_modules'])
from config import SQL_USERNAME, SQL_PASSWORD, SQL_DEV_SERVER, SQL_DEV_DATABASE, SQL_UAT_SERVER, SQL_UAT_DATABASE, SQL_PROD_SERVER, SQL_PROD_DATABASE

class connection():
    def __init__(self, user):
        
        self.username = SQL_USERNAME
        self.password = SQL_PASSWORD
        self.server = eval(f"SQL_{user}_SERVER")
        self.database = eval(f"SQL_{user}_DATABASE")
        if user == "DEV":
            t, s = self.database.split("_")
            self.database = f"{t} {s}"
        self.connection = ""

    def connect_to_server(self):
        """
        this is what my method does
        """
        retry_counter = 0
        
        server = self.server
        database = self.database
        username = self.username
        password = self.password
        while True:
            try:
                self.connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
                break
            except:
                retry_counter += 1
                if retry_counter == 5:
                    self.connection = ""
                    break
                else:
                    print("Retrying DB connection")
                    time.sleep(2)
        return self.connection
    
    def disconnect(self):
        self.connection.close()

    def get_key(self, query):
        """
        Gets key from newly created item
        """
        data = pd.read_sql(query, self.connection)
        return data

    def Read(self, query, handle_time=False):
        """
        Executes a read SQL for any given query, returns empty/none if query is invalid
        """
        if self.filter_query:
            self.connection = self.connect_to_server()
            if handle_time:
                self.connection.add_output_converter(-155, self.handle_datetimeoffset)
            data = pd.read_sql(query, self.connection)

            return data
        print("Invalid Query")

    def Execute(self, query):
        """
        Executes a query, optional to add values for inserts
        """
        primary_key = 0
        if self.filter_query:
            try:
                self.connection = self.connect_to_server()
                cursor = self.connection.cursor()
                data = cursor.execute(query)
                cursor.commit()
                #pulls the primary key from the value created
                try:
                    query = """
                    SELECT @@IDENTITY
                    """
                    primary_key = self.get_key(query)
                except Exception as e:
                    print(e)
                    print("Could not return identity, returning 0")

                cursor.close()
                self.connection.close()
                return primary_key
            except Exception as e:
                print(f"Encountered an exception while executing .. {e}")
                print("Returning 0 for the primary key...")
                return primary_key
        
        print("Invalid Query")

    def Fetch(self, query, handle_time=False):
        """
        Runs the execute command and fetches result rather than primary key
        """
        if self.filter_query:
            try:
                self.connection = self.connect_to_server()
                if handle_time:
                    self.connection.add_output_converter(-155, self.handle_datetimeoffset)
                cursor = self.connection.cursor()
                execution = cursor.execute(query)
                data = cursor.fetchall()
                return data

            except Exception as e:
                print(f"Encountered an exception while executing .. {e}")
                print("Returning Empty List...")
                return []

    def filter_query(self, query):
        """
        Checks for key words that are not allowed in SQL Queries
        By Permission of our account many of the operations we are blocking will be blocked by SQL Server.
        """
        if ";" in query:
            return False
        if "go" in query.lower():
            return False
        if "drop" in query:
            return False
        if "or" in query:
            return False

        return True

    def handle_datetimeoffset(self, dto_value):
        # ref: https://github.com/mkleehammer/pyodbc/issues/134#issuecomment-281739794
        tup = struct.unpack("<6hI2h", dto_value)  # e.g., (2017, 3, 16, 10, 35, 18, 500000000, -6, 0)
        return datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5], tup[6] // 1000,
                        timezone(timedelta(hours=tup[7], minutes=tup[8])))

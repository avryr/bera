import mysql.connector
from mysql.connector import Error

def uploadToDatabase(table_name, valuesDict):
    values = [
        valuesDict["timestamp"]['value'],
        valuesDict["temperature"]['value'],
        valuesDict["barometricPressure"]['value'], valuesDict["relativeHumidity"]['value'],
        valuesDict["dewpoint"]["value"]
    ]
    sql = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(values))})"
    try:
        query_update(sql, values)
    except Error as e:
        raise Exception(f"Database connection error: {e}")
    
def deleteFromDatabase(table_name, condition):
    sql = f"DELETE FROM {table_name} WHERE {condition}"
    try:
        query_update(sql)
    except Error as e:
        raise Exception(f"Database connection error: {e}")
    
def selectFromDatabase(table_name, condition="*"):
    sql = f"SELECT {condition} FROM {table_name}"
    try:
        return query_execute(sql)
    except Error as e:
        raise Exception(f"Database connection error: {e}")

# select or other queries 
def query_execute(sql, params=None):
    URL = "[url here]"
    DATABASE = "[database name here]"
    USER = "[username here]"
    PASSWORD = "[password here]"
    try:
        conn = mysql.connector.connect(host=URL, database=DATABASE,
                                       user=USER, password=PASSWORD)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or [])
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Error as e:
        raise Exception(f"Database connection error: {e}")
    

# insert, delete, or other modifications
def query_update(sql, params=None):
    URL = "[url here]"
    DATABASE = "[database name here]"
    USER = "[username here]"
    PASSWORD = "[password here]"
    try:
        conn = mysql.connector.connect(host=URL, database=DATABASE,
                                       user=USER, password=PASSWORD)
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        return rows_affected
    except Error as e:
        raise Exception(f"Database connection error: {e}")



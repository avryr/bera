#pip install pymongo
from pymongo import MongoClient

import mysql.connector
from mysql.connector import Error

def uploadToDatabase(collectionName, valuesDict):
    CONNECTION_STRING = "mongodb://username:password@host:port/"
    try:
        client = MongoClient(CONNECTION_STRING)
        db = client["your_database_name"]  # Access the database
        collection = db[collectionName]  # Access the collection

        document = {"timestamp": valuesDict["timestamp"]['value'],
                    "temperature": valuesDict["temperature"]['value'],
                    "barometricPressure": valuesDict["barometricPressure"]['value'],
                    "relativeHumidity": valuesDict["relativeHumidity"]['value'],
                    "dewpoint": valuesDict["dewpoint"]["value"]}
        
        inserted_id = collection.insert_one(document).inserted_id
        client.close()
        return inserted_id
    except Error as e:
        raise Exception(f"Database connection error: {e}")
    
def selectAllFromDatabase(collectionName):
    CONNECTION_STRING = "mongodb://username:password@host:port/"
    try:
        client = MongoClient(CONNECTION_STRING)
        db = client["your_database_name"]  # Access the database
        collection = db[collectionName]  # Access the collection

        docs =  list(collection.find())
        client.close()
        return docs
    except Error as e:
        raise Exception(f"Database connection error: {e}")
    


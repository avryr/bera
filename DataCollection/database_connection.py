from pymongo import MongoClient
from datetime import datetime, timezone
import os

def uploadToDatabase(collectionName, valuesDict, timestamp):
    CONNECTION_STRING = os.environ["MONGODB_URI"]
    database = os.environ["DATABASE_NAME"]

    client = MongoClient(CONNECTION_STRING) 
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    document = {
        "timestamp": timestamp,
        "temperature": valuesDict.get("temperature", {}).get("value", None),
        "barometricPressure": valuesDict.get("barometricPressure", {}).get("value", None),
        "relativeHumidity": valuesDict.get("relativeHumidity", {}).get("value", None),
        "dewpoint": valuesDict.get("dewpoint", {}).get("value", None),
        "precipitation": valuesDict.get("precipitation", {}).get("value", None)
    }
        
    inserted_id = collection.insert_one(document).inserted_id
    client.close()
    return inserted_id
    
def selectAllFromDatabase(collectionName):
    CONNECTION_STRING, database = getConnectionString.getConnectionString()
    
    client = MongoClient(CONNECTION_STRING) 
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    docs = list(collection.find())
    client.close()
    return docs

def clearCollection(collectionName):
    CONNECTION_STRING, database = getConnectionString.getConnectionString()

    client = MongoClient(CONNECTION_STRING)
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    collection.delete_many({})
    client.close()

def test_connection():
    CONNECTION_STRING, database = getConnectionString.getConnectionString()
    
    try:
        client = MongoClient(CONNECTION_STRING)
        db = client[database]  # Access the database
        client.admin.command("ping")  # Test connection
        print("Connected to MongoDB successfully!")
        client.close()
    except Exception as e:
        print(f"Connection failed: {e}")

def test_upload():
    uploadToDatabase("CWRU", {
        "timestamp": {"value": datetime.now(timezone.utc)},
        "temperature": {"value": 0.0},
        "barometricPressure": {"value": 0.0},
        "relativeHumidity": {"value": 0.0},
        "dewpoint": {"value": 0.0},
    })
    
    print(selectAllFromDatabase("CWRU"))
    clearCollection("CWRU")
    print(selectAllFromDatabase("CWRU"))


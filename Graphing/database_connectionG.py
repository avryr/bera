from pymongo import MongoClient
from datetime import datetime, timezone
import getConnectionString
    
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

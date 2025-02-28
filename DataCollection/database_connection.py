#pip install pymongo
from pymongo import MongoClient

def getConnectionString():
    return "mongodb://username:password@host:port/", "your_database_name"

def uploadToDatabase(collectionName, valuesDict):
    CONNECTION_STRING, database = getConnectionString()

    client = MongoClient(CONNECTION_STRING)
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    document = {"timestamp": valuesDict["timestamp"]['value'],
                "temperature": valuesDict["temperature"]['value'],
                "barometricPressure": valuesDict["barometricPressure"]['value'],
                "relativeHumidity": valuesDict["relativeHumidity"]['value'],
                "dewpoint": valuesDict["dewpoint"]["value"]}
        
    inserted_id = collection.insert_one(document).inserted_id
    client.close()
    return inserted_id
    
def selectAllFromDatabase(collectionName):
    CONNECTION_STRING, database = getConnectionString()
    
    client = MongoClient(CONNECTION_STRING)
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    docs =  list(collection.find())
    client.close()
    return docs


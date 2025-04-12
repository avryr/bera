from pymongo import MongoClient
from datetime import datetime, timezone
import os

# NOTE FOR FUTURE USE
# Feel free to modify the contents of these methods if switching to a new database. Currently, this is set up for
# a MongoDB database, and uses environment variables on our server where we are hosting our website to store the
# username and password to access our database.

# Alternate option:
# def getConnectionString():
#     return "mongodb+srv://[username-here]:[password-here]@[cluster-name.cluster-ID].mongodb.net", "database-Name"
# 
# You can then replace the code in between the /////// sections with:
# CONNECTION_STRING, database = getConnectionString()
#
# (Note that the cluster-name and cluster-ID can usually be found on your MongoDB page as just part of the default
# database link.)
#
# If not using a MongoDB database, that might require you to rewrite a decent portion of the overall code.


def uploadToDatabase(collectionName, valuesDict, timestamp):
    #///////////////////////
    CONNECTION_STRING = os.environ["MONGODB_URI"]
    database = os.environ["DATABASE_NAME"]
    #///////////////////////

    client = MongoClient(CONNECTION_STRING) 
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    # format the values properly from the valuesDict argument
    document = {
        "timestamp": timestamp,
        "temperature": valuesDict.get("temperature", None),
        "barometricPressure": valuesDict.get("barometricPressure", None),
        "relativeHumidity": valuesDict.get("relativeHumidity", None),
        "dewpoint": valuesDict.get("dewpoint", None),
        "precipitation": valuesDict.get("precipitation", None)
    }
        
    # insert into database
    inserted_id = collection.insert_one(document).inserted_id
    client.close() # close connection
    return inserted_id # return the index of the inserted value
    



def selectAllFromDatabase(collectionName):
    #///////////////////////
    CONNECTION_STRING = os.environ["MONGODB_URI"]
    database = os.environ["DATABASE_NAME"]
    #///////////////////////
    
    client = MongoClient(CONNECTION_STRING) 
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    docs = list(collection.find())
    client.close()
    # returns a list [] of dictionaries {}
    return docs



def clearCollection(collectionName):
    #///////////////////////
    CONNECTION_STRING = os.environ["MONGODB_URI"]
    database = os.environ["DATABASE_NAME"]
    #///////////////////////

    client = MongoClient(CONNECTION_STRING)
    db = client[database]  # Access the database
    collection = db[collectionName]  # Access the collection

    collection.delete_many({})
    client.close()




# -------------------------------------------
# Tests

def test_connection():
    #///////////////////////
    CONNECTION_STRING = os.environ["MONGODB_URI"]
    database = os.environ["DATABASE_NAME"]
    #///////////////////////
    
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
        "timestamp": datetime.now(timezone.utc),
        "temperature": 0.0,
        "barometricPressure": 0.0,
        "relativeHumidity": 0.0,
        "dewpoint": 0.0,
    }, datetime.now(timezone.utc))
    

import schedule
import TempestWeatherData
import NationalWeatherData
import database_connection
from datetime import datetime, timezone

#If you want to make your own project, all you need to do is change the values in this script
#If you want to use a different MongoDB database, make a different getConnectionString.py script.
#If you want to use a different database altogether, make a new database_connection.py script

def Start():

    # Glennan Tempest token
    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')
    # Cleveland Hopkins
    KCLE = NationalWeatherData.NationalWeatherData("KCLE")
    # Burke Lakefront
    KBKL = NationalWeatherData.NationalWeatherData("KBKL")


    # insert timestamp
    timestamp = datetime.now(timezone.utc)

    database_connection.uploadToDatabase("CWRU", CWRUData, timestamp)
    database_connection.uploadToDatabase("KCLE", KCLE, timestamp)
    database_connection.uploadToDatabase("KCLE", KBKL, timestamp)
    # ADD DATA FROM FLDIGI NOW!!!
    # database_connection.uploadToDatabase("Radio", RadioData)

    

schedule.every(30).minutes.do(Start)

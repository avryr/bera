import schedule
import TempestWeatherData
import NationalWeatherData
import database_connection

#If you want to make your own project, all you need to do is change the values in this script
#If you want to use a different MongoDB database, make a different getConnectionString.py script.

def Start():

    # Glennan Tempest token
    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')
    # Cleveland Hopkins
    KCLE = NationalWeatherData.NationalWeatherData("KCLE")
    # Burke Lakefront
    KBKL = NationalWeatherData.NationalWeatherData("KBKL")


    database_connection.uploadToDatabase("CWRU", CWRUData)
    database_connection.uploadToDatabase("KCLE", KCLE)
    # ADD DATA FROM FLDIGI NOW!!!
    # database_connection.uploadToDatabase("Radio", RadioData)

    # insert timestamp
    #NOTE: ADD TIMESTAMP TO database_connection function!!!!

schedule.every(30).minutes.do(Start)

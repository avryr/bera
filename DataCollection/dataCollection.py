import schedule
import TempestWeatherData
import NationalWeatherData
import database_connection


def Start():

    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')
    NASAData = NationalWeatherData.NationalWeatherData()

    database_connection.uploadToDatabase("CWRU", CWRUData)
    database_connection.uploadToDatabase("NASA", NASAData)
    # ADD DATA FROM FLDIGI NOW!!!

schedule.every(30).minutes.do(Start)

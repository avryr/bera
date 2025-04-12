import schedule, time
import TempestWeatherData
import NationalWeatherData
import database_connection
import fldigi_harness
from datetime import datetime, timezone

# DATA COLLECTION!
# NOTE: this is the central data collecting script. It calls a combination of the other scripts in order to organize
# and execute the proper functionality. The easiest way to change the actions executed by the program is from here.

# Same database/structure, different data sources --> change the appropriate values in this script 
# Different MongoDB database --> change the database connection url & database name. See database_connection.py for instructions
# Different non-MongoDB database --> change database_connection.py
# Different radio data collection method? Refer to/edit fldigi_harness.py

def Start():
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc)
    ip_address = "100.91.87.85" # Tailscale IP of remote host

    #Glennan Tempest module token
    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')

    #Cleveland Hopkins airport code is KCLE
    KCLE = NationalWeatherData.NationalWeatherData("KCLE")

    #Burke Lakefront airport code is KBKL
    KBKL = NationalWeatherData.NationalWeatherData("KBKL")


    # store current timestamp to standardize the timestamps in the database (helps for graphing)
    timestamp = datetime.now(timezone.utc)

    # upload to database with the appropriate collection names
    # uploadToDatabase(String collectionName, dictionary data, timestamp)
    database_connection.uploadToDatabase("CWRU", CWRUData, timestamp)
    database_connection.uploadToDatabase("KCLE", KCLE, timestamp)
    database_connection.uploadToDatabase("KCLE", KBKL, timestamp)
    # ADD DATA FROM FLDIGI
    fldigi_harness.makeMeasurement(True, timestamp, ip_address)


# Repeat the data collection every 30 mins.
schedule.every(30).minutes.do(Start)

# Start the scheduled runs. Keeps going until you manually stop it.
while True:
    schedule.run_pending()
    time.sleep(1)

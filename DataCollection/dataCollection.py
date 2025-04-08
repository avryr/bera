import schedule, time
import TempestWeatherData
import NationalWeatherData
import database_connection
import fldigi_harness
from datetime import datetime, timezone


def Start():
    # Get the current timestamp
    timestamp = datetime.now(timezone.utc)
    ip_address = "100.91.87.85" # Tailscale IP of remote host
    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')
    NASAData = NationalWeatherData.NationalWeatherData()

    database_connection.uploadToDatabase("CWRU", CWRUData, timestamp)
    database_connection.uploadToDatabase("NASA", NASAData, timestamp)
    # ADD DATA FROM FLDIGI NOW!!!
    fldigi_harness.makeMeasurement(True, timestamp, ip_address)


#Start()
schedule.every(30).minutes.do(Start)

while True:
    schedule.run_pending()
    time.sleep(1)

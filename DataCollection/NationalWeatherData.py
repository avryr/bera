#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
from datetime import datetime, timezone

import requests #library that makes the calls to the API URL and the response back from the server.

def NationalWeatherData(airportCode):

    try:
        URL = "https://api.weather.gov/stations/" + airportCode + "/observations/latest"
        #get the response from the server as a JSON file
        #open URL in browser to see full JSON file
        response = requests.get(URL) 
        #get relevant data
        forecast = response.json()['properties']

        # extract only the data we want -- feel free to go to the link below for an example from the Cleveland
        # Hopkins Airport of how these docs are formatted and what data types there are:
        # "https://api.weather.gov/stations/KCLE/observations/latest"
        weatherData = {
            "timestamp": datetime.fromisoformat(forecast['timestamp']),
            "temperature": forecast.get("temperature", {}).get("value", None),
            "dewpoint": forecast.get("dewpoint", {}).get("value", None),
            "barometricPressure": forecast.get("barometricPressure", {}).get("value", None),
            "relativeHumidity": forecast.get("relativeHumidity", {}).get("value", None),
            "precipitation": forecast.get("precipitationLast6Hours", {}).get("value", 0.0)
        }
    except: 
        #If the NWS is down or fails to sent data for some reason, store a null value instead of breaking our program
        weatherData = {
            "timestamp": datetime.fromisoformat(forecast['timestamp']),
            "temperature": None,
            "dewpoint": None,
            "barometricPressure": None,
            "relativeHumidity": None,
            "precipitation": 0.0
        }
    return weatherData

#print(getWeatherData())

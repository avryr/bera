#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
from datetime import datetime, timezone

import requests #library that makes the calls to the API URL and the response back from the server.

def NationalWeatherData(airportCode):

    #CLE Hopkins zone
    URL = "https://api.weather.gov/stations/" + airportCode + "/observations/latest"
    #Burke

    #get the response from the server as a JSON file
    #open URL in browser to see full JSON file
    response = requests.get(URL) 

    #get relevant data
    forecast = response.json()['properties']

    weatherData = {
        "timestamp": datetime.fromisoformat(forecast['timestamp']),
        "temperature": forecast['temperature']['value'],
        "dewpoint": forecast['dewpoint']['value'],
        "barometricPressure": forecast['barometricPressure']['value'],
        "relativeHumidity": forecast['relativeHumidity']['value'],
        "precipitation": forecast['precipitationLast6Hours']['value']
    }
    return weatherData

#print(getWeatherData())

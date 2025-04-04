#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
from datetime import datetime, timezone

import requests #library that makes the calls to the API URL and the response back from the server.

def NationalWeatherData():

    #CLE Hopkins zone
    URL_KCLE = "https://api.weather.gov/stations/KCLE/observations/latest"
    #Burke
    URL_KBKL = "https://api.weather.gov/stations/KBKL/observations/latest"

    #get the response from the server as a JSON file
    #open URL in browser to see full JSON file
    responseKCLE = requests.get(URL_KCLE) 
    responseKBKL = requests.get(URL_KBKL) 

    #get relevant data
    forecastKCLE = responseKCLE.json()['properties']
    forecastKBKL = responseKBKL.json()['properties']

    weatherData = {
        "KCLE": {
            "timestamp": datetime.fromisoformat(forecastKCLE['timestamp']),
            "temperature": forecastKCLE['temperature']['value'],
            "dewpoint": forecastKCLE['dewpoint']['value'],
            "barometricPressure": forecastKCLE['barometricPressure']['value'],
            "relativeHumidity": forecastKCLE['relativeHumidity']['value'],
            "precipitation": forecastKCLE['precipitationLast6Hours']['value']
        },
        "KBKL": {
            "timestamp": forecastKBKL['timestamp'],
            "temperature": forecastKBKL['temperature']['value'],
            "dewpoint": forecastKBKL['dewpoint']['value'],
            "barometricPressure": forecastKBKL['barometricPressure']['value'],
            "relativeHumidity": forecastKBKL['relativeHumidity']['value'],
            "precipitation": forecastKBKL['precipitationLast6Hours']['value']
        }
    }
    return weatherData

#print(getWeatherData())

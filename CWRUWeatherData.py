#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
# https://weatherflow.github.io/Tempest/api/

import requests #library that makes the calls to the API URL and the response back from the server.
#https://pypi.org/project/websockets/
import json

def getWeatherData():

    #Prof John Gibbons's house:
        # Station ID: 169693
        # Hub serial number: ST-00170041
        # Token: 71dda2d6-1998-4d22-899d-3d0e5baef2b2
        # devices: 136516, 403415?
    #CWRU:
        # Station ID: 86264
        # Token: bd78ca30-46d4-4407-b4c0-035bc8b045d7
    #https://tempestwx.com/station/169693/grid
    HumidityPressureURL = "https://swd.weatherflow.com/swd/rest/observations/?device_id=136516&token=71dda2d6-1998-4d22-899d-3d0e5baef2b2"

    #get the response from the server as a JSON file
    #open URL in browser to see full JSON file
    responseCWRU = requests.get(HumidityPressureURL).text
    #return responseCWRU

    #get relevant data
    parsedData = json.loads(responseCWRU)
    FeelsLike = parsedData['summary']['feels_like']
    return FeelsLike


"""
    CWRUData = {
        "CWRU": {
            "timestamp": forecastCWRU['timestamp'],
            "temperature": forecastCWRU['temperature']['value'],
            "dewpoint": forecastCWRU['dewpoint']['value'],
            "barometricPressure": forecastCWRU['barometricPressure']['value'],
            "relativeHumidity": forecastCWRU['relativeHumidity']['value']
        },
    }"""
    #return CWRUData

print(getWeatherData())

# List of devices for 169693:
"""
{
"devices":[
{"device_id":136516,"device_meta":{"agl":3.65760004520416,"environment":"outdoor","name":"ST-00170041","wifi_network_name":""},
"device_settings":{"show_precip_final":false},
"device_type":"ST",
"firmware_revision":"179",
"hardware_revision":"1",
"location_id":169693,
"serial_number":"ST-00170041"
},
{"device_id":403415,"device_meta":{"agl":1.8288,"environment":"indoor","name":"HB-00174669","wifi_network_name":""},
 "device_type":"HB",
 "firmware_revision":"316",
 "hardware_revision":"2",
 "location_id":169693,
 "serial_number":"HB-00174669"}
 ],
 "is_local_mode":false,
 "last_modified_epoch":1738445164,
 "latitude":41.32191,
 "location_id":169693,
 "longitude":-81.50481,
 "name":"N8OBJ_WS",
 "public_name":"N8OBJ_WS",
 "station_id":169693,
 "station_items":[
     {"device_id":136516,"item":"air_temperature_humidity","location_id":169693,"location_item_id":1323587,"sort":0,"station_id":169693,"station_item_id":1323587},
     {"device_id":136516,"item":"barometric_pressure","location_id":169693,"location_item_id":1323589,"sort":1,"station_id":169693,"station_item_id":1323589},
     {"device_id":136516,"item":"diagnostics","location_id":169693,"location_item_id":1323817,"station_id":169693,"station_item_id":1323817},
     {"device_id":403415,"item":"diagnostics","location_id":169693,"location_item_id":1323816,"station_id":169693,"station_item_id":1323816},
     {"device_id":136516,"item":"light","location_id":169693,"location_item_id":1323591,"sort":4,"station_id":169693,"station_item_id":1323591},
     {"device_id":136516,"item":"lightning","location_id":169693,"location_item_id":1323588,"sort":2,"station_id":169693,"station_item_id":1323588},
     {"device_id":136516,"item":"rain","location_id":169693,"location_item_id":1323590,"sort":5,"station_id":169693,"station_item_id":1323590},
     {"device_id":136516,"item":"wind","location_id":169693,"location_item_id":1323592,"sort":3,"station_id":169693,"station_item_id":1323592}
],
"station_meta":{"elevation":306.77880859375,"share_with_wf":true,"share_with_wu":true},
"timezone":"America/New_York","timezone_offset_minutes":-300
}
"""
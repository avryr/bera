#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
# https://weatherflow.github.io/Tempest/api/

import requests #library that makes the calls to the API URL and the response back from the server.
#https://pypi.org/project/websockets/
import json
from time import strftime, localtime

def getWeatherData():

    #Prof John Gibbons's house:
        #https://tempestwx.com/station/169693/grid
        # Station ID: 169693
        # Hub serial number: ST-00170041
        # Token: 71dda2d6-1998-4d22-899d-3d0e5baef2b2
        # devices: 136516 (outdoor), 403415 (indoor)
    #CWRU:
        #https://tempestwx.com/station/86264/grid
        # Station ID: 86264
        # Token: bd78ca30-46d4-4407-b4c0-035bc8b045d7
        # devices: 226978 (outdoor), 226405 (indoor)
    #GET THE LIST OF DEVICES (see bottom of file):
        #URL = "https://swd.weatherflow.com/swd/rest/stations?token=bd78ca30-46d4-4407-b4c0-035bc8b045d7"
        
    URL = "https://swd.weatherflow.com/swd/rest/observations/?device_id=226978&token=bd78ca30-46d4-4407-b4c0-035bc8b045d7"

    responseCWRU = requests.get(URL).text
    parsedData = json.loads(responseCWRU)
    observations = parsedData['obs']
    # for more obs info/structure, see link https://apidocs.tempestwx.com/reference/observation-record-format#tempest-observation
    #0 timestamp, 1 wind lull (m/s), 2 wind average (m/s), 3 wind gust (m/s), 4 wind direction (degrees),
    #5 wind sample interval (seconds), 6 pressure (mb), 7 air temperature (°C), 8 relative humidity (%),
    #9 illuminance (lux), 10 uv (index), 11 solar radiation (W/m²), 12 rain accumulation in interval (mm),
    #13 precipitation type 0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental)
    #14 lightning average distance (km), 15 lightning strike ct in interval, 16 battery (volts),
    #17 reporting interval (minutes), 18 local day rain accumulation (mm), 19 Nearcast rain accumulation (mm),
    #20 local day Nearcast rain accumulation (mm), 21 precipitation analysis type
    
    def mbTOpa(measurement):
        return measurement*100
        
    CWRUData = {
        "CWRU": {
            "timestamp": strftime('%Y-%m-%dT%H:%M:%S', localtime(observations[0][0])),
            "temperature": observations[0][7],
            "dewpoint": "N/A",
            "barometricPressure": mbTOpa(observations[0][6]),
            "relativeHumidity": observations[0][8]
        },
    }
    return CWRUData

print(getWeatherData())


#________________________________________________________________________
#
# List of devices for 169693 John Gibbons:
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

# List of devices for 86264 Glennan CWRU:
"""
{"devices":[
    {"device_id":226405,"device_meta":{"agl":1.8288,"environment":"indoor","name":"HB-00104612","wifi_network_name":""},
        "device_type":"HB",
        "firmware_revision":"194",
        "hardware_revision":"1",
        "location_id":86264,
        "serial_number":"HB-00104612"},
     {"device_id":226978,"device_meta":{"agl":32.00400039553642,"environment":"outdoor","name":"ST-00090144","wifi_network_name":""},
        "device_settings":{"show_precip_final":false},
        "device_type":"ST",
        "firmware_revision":"181",
        "hardware_revision":"1",
        "location_id":86264,"serial_number":"ST-00090144"}
],
"is_local_mode":false,
"last_modified_epoch":1666974090,
"latitude":41.50147,
"location_id":86264,
"longitude":-81.6072,
"name":"W8EDUWS",
"public_name":"W8EDU_WS",
"station_id":86264,
"station_items":[
    {"device_id":226978, "item":"air_temperature_humidity","location_id":86264,"location_item_id":713558,"sort":0,"station_id":86264,"station_item_id":713558},
    {"device_id":226978,"item":"barometric_pressure","location_id":86264,"location_item_id":713560,"sort":1,"station_id":86264,"station_item_id":713560},
    {"device_id":226978,"item":"diagnostics","location_id":86264,"location_item_id":713564,"station_id":86264,"station_item_id":713564},
    {"device_id":226405,"item":"diagnostics","location_id":86264,"location_item_id":713557,"sort":6,"station_id":86264,"station_item_id":713557},
    {"device_id":226978,"item":"light","location_id":86264,"location_item_id":713562,"sort":4,"station_id":86264,"station_item_id":713562},
    {"device_id":226978,"item":"lightning","location_id":86264,"location_item_id":713559,"sort":2,"station_id":86264,"station_item_id":713559},
    {"device_id":226978,"item":"rain","location_id":86264,"location_item_id":713561,"sort":5,"station_id":86264,"station_item_id":713561},
    {"device_id":226978,"item":"wind","location_id":86264,"location_item_id":713563,"sort":3,"station_id":86264,"station_item_id":713563}
],
"station_meta":{"elevation":207.39817810058594,"share_with_wf":true,"share_with_wu":false},
"timezone":"America/New_York","timezone_offset_minutes":-300
}
"""
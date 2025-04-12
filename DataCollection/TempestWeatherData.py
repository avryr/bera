#Relevant links
# https://justinbraun.com/python-101-pulling-the-weather-forecast-with-the-nws-api/
# http://pythonsnacks.com/p/a-guide-on-using-the-national-weather-service-api-with-python
# https://weatherflow.github.io/Tempest/api/
from datetime import datetime, timezone


import requests #library that makes the calls to the API URL and the response back from the server.
import json
from time import strftime, localtime

# Overall function to execute code in sequential order
def TempestWeatherData(token):
    deviceID = getDeviceIDFromToken(token)
    return getWeatherDataFromDevice(token, deviceID)

# Each Tempest module has several different devices. These devices measure different things, and are categorized as
# either "indoor" or "outdoor". The outdoor ones are the ones with the data we care about. We can't query the Tempest
# module as a whole for some reason (believe me, I tried), but we can query each of the individual devices attached
# to that module and have THEM send us their data. So this function gets all of the devices attached to a specific
# access token. Note that all outdoor devices seem to collect the same data, so we can just save the first one.
# If that ever changes, feel free to edit the code. 
def getDeviceIDFromToken(token):
    URL = f"https://swd.weatherflow.com/swd/rest/stations?token={token}"
    response = requests.get(URL)
    if (response.status_code != 200): #If you can't connect, you have a bad token
        raise Exception("Your token is invalid or expired.")
    parsedData = json.loads(response.text) #parse the data provided by the Tempest devices
    # The station list is buried in a bunch of nested dictionaries. Feel free to print(parsedData) if you want to 
    # take a look at the whole nested structure.
    deviceList = parsedData["stations"][0]['devices'] 
    #find the first outdoor device by iterating through list
    device = next((d for d in deviceList if d["device_meta"]["environment"] == "outdoor"), None)
    #return the list of all outdoor devices
    return device['device_id']


def getWeatherDataFromDevice(token, deviceID):
    URL = f"https://swd.weatherflow.com/swd/rest/observations/?device_id={deviceID}&token={token}"
    response = requests.get(URL).text
    parsedData = json.loads(response)
    observations = parsedData['obs']

    # for more observation info/structure, see link:
    # https://apidocs.tempestwx.com/reference/observation-record-format#tempest-observation
    #
    # Indices to reference data:
    #0 timestamp, 1 wind lull (m/s), 2 wind average (m/s), 3 wind gust (m/s), 4 wind direction (degrees),
    #5 wind sample interval (seconds), 6 pressure (mb), 7 air temperature (°C), 8 relative humidity (%),
    #9 illuminance (lux), 10 uv (index), 11 solar radiation (W/m²), 12 rain accumulation in interval (mm),
    #13 precipitation type 0 = none, 1 = rain, 2 = hail, 3 = rain + hail (experimental)
    #14 lightning average distance (km), 15 lightning strike ct in interval, 16 battery (volts),
    #17 reporting interval (minutes), 18 local day rain accumulation (mm), 19 Nearcast rain accumulation (mm),
    #20 local day Nearcast rain accumulation (mm), 21 precipitation analysis type
    
    #Unit conversions
    def mbTOpa(measurement):
        return measurement*100
        
    def getPrecipitationType(measurement):
        typeList = ["none", "Nearcast value with display on", "Nearcast value with display off"]
        return typeList[measurement]
    
    def getPrecipitationAnalysisType(measurement):
        typeList = ["none", "rain", "hail", "rain + hail"]
        return typeList[measurement]
    
    def getDewpoint(temperature, humidity):
        # https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html 
        # Simpler calculation that gives an approximation of dew point temperature if you know the observed temperature
        # and relative humidity, proposed by Mark G. Lawrence in the Bulletin of the American Meteorological Society:
        # Td = T - ((100 - RH)/5.)
        # where Td is dew point temperature (in degrees Celsius), T is observed temperature (in degrees Celsius), and 
        # RH is relative humidity (in percent). This relationship is  accurate for relative humidity values above 50%.
        return temperature - ((100 - humidity)/5)

    #Storing all the data the outdoors Tempest modules collect in a better dictionary structure.
    data = {
        "timestamp": datetime.fromisoformat(strftime('%Y-%m-%dT%H:%M:%S', localtime(observations[0][0]))),
        "windLull": observations[0][1], #"units": "m/s"
        "windSpeed": observations[0][2], #"units": "m/s"
        "windGust": observations[0][3], #"units": "m/s"
        "windDirection": observations[0][4], #"units": "degrees"
        "intervalWindSampling": observations[0][5], #"units": "secs"
        "barometricPressure": mbTOpa(observations[0][6]), #"units": "Pa"
        "temperature": observations[0][7], #"units": "degC"
        "relativeHumidity": float(observations[0][8]), #"units": "%"
        "illuminance": observations[0][9], #"units": "lux"
        "uv": observations[0][10], #"units": "index"
        "solarRadiation": observations[0][11], #"units": "W/m²"
        "rainAccumulationOverInterval": observations[0][12], #"units": "mm"
        "precipitationType": getPrecipitationType(observations[0][13]), #"units": "[type]"
        "lightningAverageDistance": observations[0][14], #"units": "[timestamp]"
        "lightningStrikeCountOverInterval": observations[0][15], #"units": "km"
        "battery": observations[0][16], #"units": "V"
        "interval": observations[0][17]*60, #"units": "secs"
        "rainAccumulationLastDay": observations[0][18], #"units": "mm"
        "nearcastRainAccumulation": observations[0][19], #"units": "mm"
        # If we want a different measurement of precipitation, just change this back to "nearcastRainAccumulationLastDay"
        # and change the one you want to "precipitation"
        "precipitation": observations[0][20], #nearcastRainAccumulationLastDay
        "precipitationAnalysisType": getPrecipitationAnalysisType(observations[0][21]), #"units": "[timestamp]"
        "dewpoint": getDewpoint(observations[0][7], observations[0][8]) #"units": "degC"
    }

    return data

#________________________________________________________________________
# If you just want to run this program by itself and get the Tempest data, you can do so.
def main():
    token = input("Please enter the tempest Auth Token: ")
    data = TempestWeatherData(token)
    print(data)
    return data

if __name__ == "__main__":
    main()


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
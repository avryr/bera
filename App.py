import processData
import time
import schedule


def Start():
    locationList = ["CWRU", "NASA"]
    parameterList = ["temperature", "barometricPressure", "relativeHumidity", "dewpoint"]

    processData.CollectData()
    processData.Graph(locationList, parameterList)
    

schedule.every(30).minutes.do(Start)

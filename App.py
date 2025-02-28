import processData
import time


def Start():
    locationList = ["CWRU", "NASA"]
    parameterList = ["temperature", "barometricPressure", "relativeHumidity", "dewpoint"]

    flag = False
    duration = 0
    while flag == False:
        try:
            duration = int(input("How many seconds do you want to run this program? "))
            flag = True
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        processData.CollectData()
        processData.Graph(locationList, parameterList)
        time.sleep(1)
        


Start()
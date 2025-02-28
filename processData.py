import TempestWeatherData
import NationalWeatherData
import database_connection
import matplotlib.pyplot as plt
import datetime

def CollectData():
    CWRUData = TempestWeatherData.TempestWeatherData('bd78ca30-46d4-4407-b4c0-035bc8b045d7')
    NASAData = NationalWeatherData.NationalWeatherData()

    database_connection.uploadToDatabase("CWRU", CWRUData)
    database_connection.uploadToDatabase("NASA", NASAData)
    # ADD DATA FROM FLDIGI NOW!!!



def Graph(locationList, parameterList):

    # Create subplots for the graphs
    fig, axs = plt.subplots((len(parameterList) + 1) // 2, 2, figsize=(10, 8))  # 2 rows, 2 columns for 4 graphs
    axs = axs.ravel()  # Flatten the array of axes for easier indexing

    # Set the interactive mode to update the plots
    plt.ion()

    for loc in range(len(locationList)):
        for p in range(len(parameterList)):
            rawData = database_connection.selectAllFromDatabase(locationList[loc])

            timestamps = [datetime.datetime.strptime(doc["timestamp"], "%Y-%m-%d %H:%M:%S") for doc in rawData]
            collectedData = [doc[parameterList[p]] for doc in rawData]  # Adjust key as needed

            updateSubplot(axs[p], timestamps, collectedData, parameterList[p], loc)
    # Show the plot
    plt.draw()
    plt.show()  # Keep the plot open after the loop


def updateSubplot(ax, x, y, yParam, graphCount):
    if graphCount == 0:
        ax.clear()

    # Plot the data
    #plt.figure(figsize=(10, 5))
    ax.plot(x, y, marker=".", linestyle="-", color="b", label=yParam)

    if graphCount == 0:
        # Formatting the plot
        ax.set_xlabel("Timestamp")
        ax.set_ylabel(yParam)  # Adjust unit as needed
        ax.set_title(yParam+" over Time")
        ax.set_xticks(rotation=45)  # Rotate x-axis labels for better readability
        ax.legend()
        ax.grid(True)

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
    fig, axs = plt.subplots(round(parameterList / 2) + parameterList % 2, 2, figsize=(10, 8))  # 2 rows, 2 columns for 4 graphs
    axs = axs.ravel()  # Flatten the array of axes for easier indexing

    # Set the interactive mode to update the plots
    plt.ion()

    for param in range(len(parameterList)):
        for loc in range(len(locationList)):
            rawData = database_connection.selectFromDatabase(locationList[loc], "timestamp, " + parameterList[param])

            timestamps = [datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rawData]  # Adjust format if needed
            collectedData = [row[1] for row in rawData]
            updateSubplot(axs[param], timestamps, collectedData, parameterList[param], loc, len(locationList))
    plt.show()  # Keep the plot open after the loop


def updateSubplot(ax, x, y, yParam, graphCount, totalGraphs):
    if graphCount == 0:
        ax.clear

    # Plot the data
    #plt.figure(figsize=(10, 5))
    ax.plot(x, y, marker=".", linestyle="-", color="b", label=yParam)

    if graphCount == totalGraphs -1:
        # Formatting the plot
        ax.xlabel("Timestamp")
        ax.ylabel(yParam)  # Adjust unit as needed
        ax.title(yParam+" over Time")
        ax.xticks(rotation=45)  # Rotate x-axis labels for better readability
        ax.legend()
        ax.grid(True)

        # Show the plot
        plt.draw()

import database_connection
import matplotlib.pyplot as plt
import datetime


def GraphWeatherData(ax, locationList, parameter):

    for loc in range(len(locationList)):
        rawData = database_connection.selectAllFromDatabase(locationList[loc])

        timestamps = [datetime.datetime.strptime(doc["timestamp"], "%Y-%m-%d %H:%M:%S") for doc in rawData]
        collectedData = [doc[parameter] for doc in rawData]  # Adjust key as needed

        ax.plot(timestamps, collectedData, marker=".", linestyle="-")

     # Formatting the plot
    ax.xlabel("Timestamp")
    ax.ylabel(parameter)  # Adjust unit as needed
    ax.title(parameter + " Over Time")
    ax.xticks(rotation=45)  # Rotate x-axis labels for better readability
    ax.legend()
    ax.grid(True)
    ax.draw()
    ax.show()  # Keep the plot open after the loop
    
def GraphBitrateData(ax):
    rawData = database_connection.selectAllFromDatabase("Radio")
    timestamps = [datetime.datetime.strptime(doc["timestamp"], "%Y-%m-%d %H:%M:%S") for doc in rawData]
    collectedData = [doc["bitErrors"] for doc in rawData]  # Adjust key as needed
    ax.plot(timestamps, collectedData, marker=".", linestyle="-")

     # Formatting the plot
    ax.xlabel("Timestamp")
    ax.ylabel("Num Bit Errors")  # Adjust unit as needed
    ax.title("Bit Error Rate" + " Over Time")
    ax.xticks(rotation=45)  # Rotate x-axis labels for better readability
    ax.legend()
    ax.grid(True)
    ax.draw()
    ax.show()  # Keep the plot open after the loop
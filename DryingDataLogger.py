# Imports
import time
import os
import RPi.GPIO as GPIO
import datetime
import DAQ

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Constants
ambientSensorPin = 4
filename = 'Data'
filenameSuffix = '.txt'
moistureSensorQuantity = 8
dataPointsPerHour = 60.0 # Up to 120 per hour (minimum of 30 second delay before reading data)
delayBeforeReadingData = 10 # Seconds
secondsPerPoint = 60.0*60.0/float(dataPointsPerHour)

# Create new data file 
filename = DAQ.safeFilename(filename, filenameSuffix)
headerString = 'Date and Time, Nominal Minutes, Temp [C], Humidity, Brick1, Brick2, Brick3, Brick4, Brick5, Brick6, Brick7, Brick8'
DAQ.safeWriteTextToFile(filename, headerString)
print(headerString)

# Initialize time and date
startDate = datetime.datetime.today()
DAQ.initializeADC()
# Loop and collect the data
shouldContinue = True
isEven = False
nominalTestMinutes = 0

while shouldContinue == True:
    nominalTestMinutes = nominalTestMinutes + 60.0/dataPointsPerHour
    dataPointStartDateTime = datetime.datetime.today()
    nextDataPointTime = dataPointStartDateTime + datetime.timedelta(seconds=secondsPerPoint)
    
    if isEven == True:
        isEven = False
    else:
        isEven = True
    #print("Getting ambient data")
    (temperature, humidity) = DAQ.getEnvironmentData(ambientSensorPin)
    #print("Getting moisture data")
    moistureSensorValues = DAQ.getMoistureData(isEven,moistureSensorQuantity, delayBeforeReadingData) 
    
    currentdatetime = datetime.datetime.today()
    timeSinceStarting = currentdatetime - startDate

    dateTimeString = currentdatetime.isoformat(' ')

    dataString = dateTimeString + ', ' + repr(nominalTestMinutes) + ', ' + repr(temperature) + ', ' + repr(humidity)
    for i in range(moistureSensorQuantity):
        dataString = dataString + ', ' + repr(moistureSensorValues[i])

    DAQ.safeWriteTextToFile(filename, dataString)
    print(dataString)
    dataString = ""
    
    if isEven == True:
        isEven = False
    else:
        isEven = True
        
    # Reverse polarity on the sensors for euqal duration to minimize galvanic corrosion
    DAQ.getMoistureData(isEven,moistureSensorQuantity, delayBeforeReadingData) 

    now = datetime.datetime.today()

    #print("About to wait for next data point")
    while now < nextDataPointTime:
        now = datetime.datetime.today()
    #print("About to start new data point")

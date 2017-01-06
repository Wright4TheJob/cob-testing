# Imports
import time
import os
import RPi.GPIO as GPIO
from datetime
import DAQ

GPIO.setmode(GPIO.BCM)

# Constants
ambientSensorPin = 4
filename = 'Data'
filenameSuffix = '.txt'
moistureSensorQuantity = 8
dataPointsPerHour = 100.0 # Up to 120 per hour (minimum of 30 second delay before reading data)
delayBeforeReadingData = 0.5 # Minutes

# Create new data file 
filename = DAQ.safeFilename(filename, filenameSuffix)
headerString = 'Date and Time, Nominal Minutes, Temp [C], Humidity, Brick1, Brick2, Brick3, Brick4, Brick5, Brick6, Brick7, Brick8'
DAQ.safeWriteTextToFile(filename, headerString)
print(headerString)
# Initialize time and date
startDate = datetime.datetime.today()

# Loop and collect the data
shouldContinue = True
isEven = False
nominalTestMinutes = 0

while shouldContinue == True:
    nominalTestMinutes = nominalTestMinutes + dataPointsPerHour/60.0
    dataPointStartDateTime = datetime.datetime.today()
    nextDataPointTime = dataPointStartDateTime + datetime.timedelta(minutes=60.0/dataPointsPerHour)
    
    if isEven == True:
        isEven = False
    else:
        isEven = True
        
    (temperature, humidity) = DAQ.getEnvironmentData(ambientSensorPin)
    delayDuration = delayBeforeReadingData*60.0
    moistureSensorValues = DAQ.getMoistureData(isEven,moistureSensorQuantity, delayDuration) 
    
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
    DAQ.getMoistureData(isEven,moistureSensorQuantity, delayDuration) 

    while now < nextDataPointTime:
        now = datetime.datetime.now()


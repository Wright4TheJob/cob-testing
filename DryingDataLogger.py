import time
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Collect data point from temp/humidity sensor
def getEnvironmentData():

    sensorPin = 4
    sensor = Adafruit_DHT.AM2302
    
    humidity, tempC = Adafruit_DHT.read_retry(sensor, sensorPin)
    
    return (tempC, humidity)

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    # Read data from ADC, with 8 possible channels
    # adcnum - the channel to read from
    # clockpin - pin location of clock output
    # mosipin - pin location of mosi output
    # misopin - pin location of miso input
    # cspin - pin location of cs output
    
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin,True) # Bring CS high

    GPIO.output(clockpin, False) # Bring clock low
    GPIO.output(cspin, False) # Bring CS low

    commandout = adcnum
    commandout |= 0x18 # Start bit + single-ending bit
    commandout <<= 3 # Send only 5 bits now

    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        # Cycle clock between iterations of for loop
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # Read in one empty bit, one null bit and 10 adc bits
    for i in range(12):
        # Cycle clock to advance to next bit
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout|= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1 # First bit is null so drop it
    return adcout # Returns floating point value for bit-wise collected number
        

def getMoistureData(isEven):
    # constants
    spiClock = 18
    spiMiso = 23
    spiMosi = 24
    spiCs = 25

    probeLine1 = 17
    probeLine2 = 22
    n = 8

    #GPIO initialization
    GPIO.setup(spiMosi, GPIO.OUT)
    GPIO.setup(spiMiso, GPIO.IN)
    GPIO.setup(spiClock, GPIO.OUT)
    GPIO.setup(spiCs, GPIO.OUT)

    GPIO.setup(probeLine1, GPIO.OUT)
    GPIO.setup(probeLine2, GPIO.OUT)
    
    sensorVoltages = [0.0]*8
    if isEven == True:
        # Turn on sensors - set transistor pin x high
        print('Turning on even side sensors')
        GPIO.output(probeLine1, True)
    else:
        # Turn on sensors - set transistor pin y high
        print('Turning on odd side sensors')
        GPIO.output(probeLine2, True)

    # Let everything equalize in soil before taking data
    time.sleep(5)

    # Take data
    for sensor in range(n):
        sensorVoltages[sensor] = readadc(sensor, spiClock, spiMosi, spiMiso, spiCs)
        print('Collecting Sensor ' + repr(sensor) + ' data')

    # Set both transistor pins low
    GPIO.output(probeLine1, False)
    GPIO.output(probeLine2, False)
    
    return sensorVoltages

##########################################################
# -- Main Script -- #

# Imports
import os
import time
from datetime import datetime

# Constants

# Create new data file without overwriting old one
validName = False
filename = 'Data.txt'
increment = 0
while validName == False:
    if os.path.isfile(filename):
        increment = increment+1
        filename = 'Data' + repr(increment) + '.txt'
    else:
        validName = True

# Open file and write header
file = open(filename,'w')
file.write('Date and Time, Nominal Minutes, Temp [C], Humidity, Brick1, Brick2, Brick3, Brick4, Brick5, Brick6, Brick7, Brick8 \n')
file.close()
# Initialize time and date
startDate = datetime.today()

# Loop and collect the data
shouldContinue = True
isEven = False
nominalTestMinutes = 0

while shouldContinue == True:
    nominalTestMinutes = nominalTestMinutes + 1
    currentdatetime = datetime.today()
    timeSinceStarting = currentdatetime - startDate

    if isEven == True:
        isEven = False
    else:
        isEven = True
        
    (temperature, humidity) = getEnvironmentData()
    moistureSensorValues = getMoistureData(isEven) # includes 5 second delay

    dateTimeString = currentdatetime.isoformat(' ')

    with open(filename,"a") as dataFile:
        dataFile.write(dateTimeString + ', ' + repr(nominalTestMinutes) + ', ' + repr(temperature) + ', ' + repr(humidity))
        for i in range(8):
            dataFile.write(', ' + repr(moistureSensorValues[i]))
        dataFile.write('\n')

    time.sleep(55)
    

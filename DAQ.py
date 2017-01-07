import time
import os
import RPi.GPIO as GPIO
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

def safeFilename(baseFilename, suffix):
    filename = baseFilename
    validName = False
    increment = 0
    while validName == False:
        if os.path.isfile(filename):
            increment = increment+1
            filename =  baseFilename+ repr(increment) + suffix
        else:
            validName = True
    return filename

def safeWriteTextToFile(filename, text):
    # Accepts any string. Automatically add newline characters to the end. Closes the file at the end of writing
    file = open(filename,"a")
    text = text + '\n'
    file.write(text)
    file.close()

# Collect data point from temp/humidity sensor
def getEnvironmentData(pin):

    sensor = Adafruit_DHT.AM2302
    
    humidity, tempC = Adafruit_DHT.read_retry(sensor, pin)
    
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
        

def initializeADC():
    # constants
    spiClock = 18
    spiMiso = 23
    spiMosi = 24
    spiCs = 25

    probeLine1 = 17
    probeLine2 = 22

    #GPIO initialization
    GPIO.setup(spiMosi, GPIO.OUT)
    GPIO.setup(spiMiso, GPIO.IN)
    GPIO.setup(spiClock, GPIO.OUT)
    GPIO.setup(spiCs, GPIO.OUT)

    GPIO.setup(probeLine1, GPIO.OUT)
    GPIO.setup(probeLine2, GPIO.OUT)
    
def getMoistureData(isEven,n, delay):
    # constants
    spiClock = 18
    spiMiso = 23
    spiMosi = 24
    spiCs = 25

    probeLine1 = 17
    probeLine2 = 22

    sensorVoltages = [0.0]*8
    if isEven == True:
        # Turn on sensors - set transistor pin x high
        #print('Turning on even side sensors')
        GPIO.output(probeLine1, True)
    else:
        # Turn on sensors - set transistor pin y high
        #print('Turning on odd side sensors')
        GPIO.output(probeLine2, True)

    # Let everything equalize in soil before taking data
    #print("Waiting before taking data")
    time.sleep(delay)
    #print("About to take data")
    
    # Take data
    for sensor in range(n):
        sensorVoltages[sensor] = readadc(sensor, spiClock, spiMosi, spiMiso, spiCs)
        #print('Collecting Sensor ' + repr(sensor) + ' data')

    #print("Took data")
    # Set both transistor pins low
    GPIO.output(probeLine1, False)
    GPIO.output(probeLine2, False)
    
    return sensorVoltages

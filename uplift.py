import RPi.GPIO as GPIO
import time

class UpliftDesk:
    delay = 0.2 # how long to "hold" the button down when simulating an up/down press
    pinup = 18
    pindown = 22
    def __init__(self, pinup, pindown):
        self.pinup = pinup
        self.pindown = pindown
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pinup, GPIO.OUT) 
        GPIO.setup(self.pindown, GPIO.OUT) 
        GPIO.output(self.pinup,True)
        GPIO.output(self.pindown,True)
    def up(self):
        GPIO.output(self.pinup, False)
        time.sleep(self.delay)
        GPIO.output(self.pinup,True)
    def down(self):
        GPIO.output(self.pindown, False)
        time.sleep(self.delay)
        GPIO.output(self.pindown,True)

uplift = UpliftDesk(18,22)

##Define a function named Blink()
def Blink(numTimes,speed):
    for i in range(0,numTimes):## Run loop numTimes
        print "Iteration " + str(i+1)## Print current loop
        uplift.up()
        time.sleep(speed)## Wait
        uplift.down()
        time.sleep(speed)## Wait
    print "Done" ## When loop is complete, print "Done"


## Start Blink() function. Convert user input from strings to numeric data types and pass to Blink() as parameters
Blink(10,10)

GPIO.cleanup()
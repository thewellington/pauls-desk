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
    def up(self, steps = 1):
        GPIO.output(self.pinup, False)
        time.sleep(self.delay * steps)
        GPIO.output(self.pinup,True)
    def down(self, steps = 1):
        GPIO.output(self.pindown, False)
        time.sleep(self.delay * steps)
        GPIO.output(self.pindown,True)


import uplift

desk = uplift.UpliftDesk(18,22)

##Define a function named Blink()
def Blink(numTimes,speed):
    for i in range(0,numTimes):## Run loop numTimes
#        print "Iteration " + str(i+1)## Print current loop
        desk.up()
        time.sleep(speed)## Wait
        desk.down()
        time.sleep(speed)## Wait
#    print "Done" ## When loop is complete, print "Done"


## Start Blink() function. Convert user input from strings to numeric data types and pass to Blink() as parameters
Blink(10,10)

GPIO.cleanup()
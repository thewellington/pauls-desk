import uplift

desk = uplift.UpliftDesk(18,22)

def Blink(numTimes,speed):
    for i in range(0,numTimes):
#        print "Iteration " + str(i+1)
        desk.up()
        time.sleep(speed)
        desk.down()
        time.sleep(speed)
#    print "Done"


Blink(10,10)

GPIO.cleanup()
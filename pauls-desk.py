#import uplift
import hipchat
import time
import thread

def input_thread(L):
    raw_input()
    L.append(None)
            
#desk = uplift.UpliftDesk(18,22)


'''
def Blink(numTimes,speed):
    for i in range(0,numTimes):
#        print "Iteration " + str(i+1)
        desk.up()
        time.sleep(speed)
        desk.down()
        time.sleep(speed)
#    print "Done"
'''

def msg_hello(message, control):
    return "Hi!"

def msg_status(message, control):
    if not control:
        return ""
    return "This static text says that all systems are good."
    
def msg_ip(message, control):
    if not control:
        return ""
    return "Here's my IP address: <calculate something, dummy>"

responses = {"hello": msg_hello,
            "hi": msg_hello,
            "ip info": msg_ip,
            "status": msg_status}


list = ""
for u in hipchat.friends:
    if (len(list)>0):
        list += ", "
    list += u.name

list = "Hello, my friends: " + list

print list

print "My user name is: " + hipchat.api_user
    
#Blink(10,10)

#GPIO.cleanup()

def msg_maker(msg):
    return "Responding to: " + str(msg)

control = hipchat.HipchatRoom(hipchat.control_room)

control.set_response_list(responses)

control.publish_status()

control.watch_room()

waitqueue = []
thread.start_new_thread(input_thread, (waitqueue,))
while 1:
    time.sleep(.1)
    if waitqueue: break

print "Waiting for threads to finish..."
control.stop_watching()
print "Threads finished. Ending Program."

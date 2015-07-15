import hipchat
import time
import thread
import yaml
import sys
import random

try:
    import uplift
except ImportError:
    sys.stderr.write("Uplift failed to import. Desk functions disabled.")

class BadDesk:
    def up(self):
        sys.stderr.write("Attempting to move desk up, but module not"
                " imported.")
    def down(self):
        sys.stderr.write("Attempting to move desk down, but module not"
                " imported.")

def input_thread(L):
    raw_input()
    L.append(None)

if 'uplift' in sys.modules:
    desk = uplift.UpliftDesk(18,22)
else:
    desk = BadDesk()

try:
    f = open('responses.yml')
    response_data = yaml.load(f)
    f.close()
except:
    sys.stderr.write("Error loading response.yml file.")
    response_data = []
    raise
    
def y(needle):
    global response_data
    try:
        response = response_data[needle]
        if type(response) is str:
            return response
        if type(response) is type([]):
            print "list"
            return random.choice(response)
        print "Unknown type of response object: " + str(type(response))
        return ""
    except:
        print "YAML error reading response for " + str(needle)
        return ""

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

def msg_hello(needle, message):
    return "Hi!"

def msg_default(needle, message):
    return y(needle)
    
def msg_status(needle, message):
    if not message.is_control:
        return ""
    return "This static text says that all systems are good."
    
def msg_ip(needle, message):
    if not message.is_control:
        return ""
    return "Here's my IP address: <calculate something, dummy>"

responses = {"hello": msg_default,
            "hi": msg_default,
            "hola": msg_default,
            "ip info": msg_ip,
            "status": msg_status,
            "default": msg_default}


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

control.watch_room()

waitqueue = []
thread.start_new_thread(input_thread, (waitqueue,))
while 1:
    time.sleep(.1)
    if waitqueue: break

print "Waiting for threads to finish..."
control.stop_watching()
print "Threads finished. Ending Program."

import hipchat
import time
import thread
import yaml
import sys
import random
import socket

try:
    import uplift
except ImportError:
    print "Uplift failed to import. Desk functions disabled."

class BadDesk:
    def up(self):
        print ("Attempting to move desk up, but module not"
                " imported.")
    def down(self):
        print ("Attempting to move desk down, but module not"
                " imported.")

def input_thread(L):
    raw_input()
    L.append(None)

if 'uplift' in sys.modules:
    desk = uplift.UpliftDesk(18,22)
else:
    desk = BadDesk()

def update_response_yaml():
    try:
        f = open('responses.yml')
        response_data = yaml.load(f)
        f.close()
        return response_data
    except:
        print "*** Error loading response.yml file."
        return []
        
    
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

def msg_default(needle, message):
    return y(needle)

def msg_status(needle, message):
    if not message.is_control:
        return ""
    return "This static text says that all systems are good."
    
def msg_network(needle, message):
    if not message.is_control:
        return ""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = s.getsockname()[0]
    s.close()
    return "IP Address: " + str(ip)

def msg_refresh(needle, message):
    if not message.is_control:
        return ""
    global response_data
    response_data = update_response_yaml()
    for rd in response_data:
        if rd not in responses:
            responses[rd] = msg_default
    
    hipchat.friends = hipchat.get_friends()
    return y("refresh")
    
def msg_friends(needle, message):
    if not message.is_control:
        return ""
    hipchat.friends = hipchat.get_friends()
    list = ""
    for u in hipchat.friends:
        if (len(list)>0):
            list += ", "
        list += u.name

    list = y("friends") + list

    return list


responses = {"network": msg_network,
            "status": msg_status,
            "refresh": msg_refresh,
            "friends": msg_friends}

print "My user name is: " + hipchat.api_user
    
#Blink(10,10)

#GPIO.cleanup()


response_data = update_response_yaml()

for rd in response_data:
    if rd not in responses:
        responses[rd] = msg_default

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

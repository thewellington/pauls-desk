import hipchat
import time
import thread
import yaml
import sys
import random
import socket
import datetime
import threading

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

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = s.getsockname()[0]
    s.close()
    return ip
    
def msg_default(needle, message):
    return y(needle)

def msg_status(needle, message):
    if not message.is_control:
        return ""
    return "This static text says that all systems are good."
    
def msg_network(needle, message):
    if not message.is_control:
        return ""
    return "IP Address: " + str(get_ip_address())

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

def msg_up(needle, message):
    hipchat.notify_control("Moving desk up...")
    uplift.up
    return y("up")

def msg_down(needle, message):
    hipchat.notify_control("Moving desk down...")
    uplift.down
    return y("down")
    
def msg_rooms(needle,message):
    if not message.is_control:
        return ""
    list = ""
    for r in room_objects:
        if (len(list)>0):
            list += ", "
        list += r.name

    list = "Rooms I'm watching: " + list

    return list

responses = {"network": msg_network,
            "status": msg_status,
            "refresh": msg_refresh,
            "friends": msg_friends,
            "up": msg_up,
            "down": msg_down}


def evaluate_existing_room(room):
    print "(" + str(hipchat.rate_limit) + ") Evaluating room: " + str(room)

    room.lastevaluated = datetime.datetime.utcnow()
    
    if room.lastmsg != None:
        if datetime.date.utcnow() - room.lastmsg < datetime.timedelta(hours=1):
            room.watch_room()
            return  # Recent-ish messages, let's leave this alone
    
    la = room.last_active()
    if la == datetime.date.min:
        hipchat.notify_control("Considering archive of room: " + str(room) + ". Last accessed: Never.")
        return
    elif (datetime.datetime.utcnow() - la) > datetime.timedelta(180):
        hipchat.notify_control("Considering archive of room: " + str(room) + ". Last accessed: " + str(la) + ".")
        return
        
    if (datetime.datetime.utcnow() - la) < datetime.timedelta(hours=1):
        room.watch_room()
    else:
        room.stop_watching()

def evaluate_rooms():
    global alive
    while alive:
        for rm in room_objects:
            if not alive:
                return
            while hipchat.rate_limit < 20 and alive:
                time.sleep(5)
            evaluate_existing_room(rm)
            for x in range (0,65): # just over a minute
                time.sleep(1)
                if not alive:
                    return

        num = 0
        for r in room_objects:
            if room_objects.active:
                num = num + 1
                
        interval = int((5*60)/80) * num
        default_interval = 15
        if interval > default_interval:
            print "Setting room check intervals to " + str(interval) + " seconds."
            hipchat.notify_control("Check interval moving to "+str(interval) +" seconds.")
        for r in room_objects:
            r.check_interval = max(default_interval, interval)


    
print "My user name is: " + hipchat.api_user
    
#Blink(10,10)

response_data = update_response_yaml()

for rd in response_data:
    if rd not in responses:
        responses[rd] = msg_default

control = hipchat.HipchatRoom(hipchat.control_room)

control.set_response_list(responses)

hipchat.notify_control("Starting up chatbot from IP address: " + str(get_ip_address()))

control.watch_room()

room_objects = []

for x in hipchat.rooms:
    room = hipchat.HipchatRoom(x)
    room.set_response_list(responses)
    room.lastevaluated = datetime.datetime.utcnow()
    room_objects.append(room)
    
alive = True
waitqueue = []
thread.start_new_thread(input_thread, (waitqueue,))
evaluate_thread = threading.Thread(target=evaluate_rooms)

evaluate_thread.daemon = True
evaluate_thread.start()

while 1:
    time.sleep(.1)
    if waitqueue: break

alive = False
print "Waiting for threads to finish..."
control.stop_watching()
for r in room_objects:
    r.stop_watching()
for r in room_objects:
    r.join()


evaluate_thread.join()

hipchat.notify_control("Goodnight.")
print "Threads finished. Ending Program."

GPIO.cleanup()

"""Hipchat objects to chat with a room and get basic info from the service."""
# import necessary modules

import sys
#import traceback
#import getopt
import json
import datetime
#import dateutil
import threading
import time
import re

try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    sys.stderr.write("You do not have the 'requests' module installed. "
        "Please see http://docs.python-requests.org/en/latest/ for more "
        "information.")
    exit(1)

try:
    import yaml
except ImportError:
    sys.stderr.write("You do not have the 'yaml' module installed. "
        "Please see http://pyyaml.org/wiki/PyYAMLDocumentation for more "
        "information.")
    exit(1)


class HipchatRoom:

    """A Hipchat Room, and the ability to watch the room for messages."""

    def __init__(self, roomid):
        """Make a new HipchatRoom with basic info."""
        self.roomid = roomid
        self.lastmsg = None
        self.active = False
        self.check_interval = 15
        self.thread = None
        self.control_room = False
        if self.roomid == control_room:
            self.control_room = True
        self.response_list = {}
        try:
            self.name = rooms[self.roomid]
        except KeyError:
            self.name = get_room_name(self.roomid)
        self.lastevaluated = None

    def __str__(self):
        """Convert room to string.

        Return just the name of the room.
        """
        return self.name

    def last_active(self):
        """Get last active timestamp."""
        return get_room_last_active(self.roomid)

    def participants(self):
        """Get room participants."""
        return list_room_participants(self.roomid)

    def set_response_list(self, responses):
        """Save response list object."""
        self.response_list = responses

    def watch_room(self):
        """Start a thread to watch this room."""
        if self.active == True:
            return
        self.check_messages()
        self.active = True
        self.thread = threading.Thread(target=self.room_watcher)
        self.thread.daemon = True
        self.thread.start()
        notify_room(control_room, "Begun watch of room: " + str(self.name))

    def stop_watching(self):
        if self.active == False:
            return
        self.active = False
        notify_room(control_room, "Stopping watch of room: " + str(self.name))

    def join(self):
        if self.thread is None:
            return
        if self.thread.isAlive():
            self.thread.join()

    def room_watcher(self):
        """Thread function to actually watch the room."""
        while self.active:
            while rate_limit < 15 and self.active and not self.control_room:
                time.sleep(self.check_interval)
            print "(" + str(rate_limit) + ") Checking messages in room: " + str(self.name)
            self.check_messages()
            time.sleep(self.check_interval)

    def check_messages(self):
        """Look for new messages in the room. Called from the thread (room_watcher)."""
        if self.lastmsg == None:
            messages = get_latest_message(self.roomid)
            self.lastmsg = messages[0].date
            return
        messages = get_room_history(self.roomid)
        if messages is None:
            print "Check of room " + self.name + " resulted in no reply. Rate limit hit?"
            return
        response = ""
        new_date = self.lastmsg
        for one_message in messages:
            if one_message.fromid == api_user_id:
                continue
            new_date = self.lastmsg
            if self.lastmsg > one_message.date:
                pass
            elif new_date < one_message.date:
                new_date = max(one_message.date, new_date)
                result = ""
                print str(one_message.date) + " : " + str(one_message)
                result = self.process_one_message(one_message)
                if result == "":
                    print "\tResult: ignored"
                else:
                    response = result
                    print "\tResult: " + result.encode("utf-8")
        if response != "":
            notify_room(control_room, "(Room: " + self.name + ") " + response)
#            notify_room(self.roomid, response)
        self.lastmsg = new_date

    def process_one_message(self, message):
        """Take one message posted and check to see if we want to reply to it."""
        word_list = re.split('\W+',message.msg.lower())
        for needle in self.response_list:
            if needle.lower() in word_list:
                print "\tFound needle: " + needle
                response = self.response_list[needle](needle, message)
                return response
        return ""



class HipchatMessage:

    """One Hipchat Message."""

    def __init__(self, fromid, date, msg):
        """Create new message with basic starting info."""
        self.fromid = fromid
        # sample date to parse: 2015-04-24T22:10:44.146716+00:00
        self.date = datetime.datetime.strptime(date,
                            "%Y-%m-%dT%H:%M:%S.%f+00:00")
        self.msg = msg
        self.id = ''
        self.room = 0

    def __str__(self):
        """Convert message to a string.

        This simply returns the message itself, without meta data.
        """
        return self.msg

    def is_control(self):
        """Return true if this message from the command and control room."""
        if self.room == control_room:
            return True
        return False

    def is_friend(self):
        """Return true if this message was sent from a friend/admin."""
        if self.fromid in friends:
            return True
        return False


class HipchatUser:

    """Basic info on a Hipchat User."""

    def __init__(self, user_id, name, mentionname):
        """Create new user with userid, name, and mentionname."""
        self.id = user_id
        self.name = name
        self.mentionname = mentionname

    def __str__(self):
        """Convert object to string.

        Return just the user name, without extra info.
        """
        return self.name


def _api_get(url, data=None):
    url, data = url, data
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json',
                          'Authorization': auth}
    response = requests.get(url, headers=requisite_headers)
    return response.status_code, response.headers, response.text


# def _api_put(url, data):
#     url, name, passwd = url, user, token
#     requisite_headers = {'Accept': 'application/json',
#                           'Content-Type': 'application/json'}
#     auth = (name, passwd)
#     response = requests.put(url, headers=requisite_headers,
#                                 auth=auth, params=data)
#     return response.status_code, response.headers, response.text


def _api_post(url, data):
    url, data = url, data
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json',
                          'Authorization': auth}
    response = requests.post(url, headers=requisite_headers, data=data)
    return response.status_code, response.headers, response.text


# def _api_del(argv):
#     url, name, passwd = argv[0], argv[1], argv[2]
#     requisite_headers = {'Accept': 'application/json',
#                           'Content-Type': 'application/json'}
#     auth = (name, passwd)
#     response = requests.delete(url, headers=requisite_headers, auth=auth)
#     return response.status_code, response.headers, response.text

#    def load_file(fname):
#        with open(fname) as f:
#            return f.read()


def rest(req, url, data=None):
    global rate_limit
    url = base_url + url
#    print url
    if 'HTTPS' not in url.upper():
        print ("Secure connection required: HTTP not valid, "
                    "please use HTTPS or https")
#        rest_usage()
    cmd = req.upper()
    if cmd not in cmds.keys():
#        rest_usage()
        return None
    status, headers, body = cmds[cmd](url, data)
    try:
        rate_limit = int(headers['x-ratelimit-remaining'])

        epoch = datetime.datetime.utcnow()
        reset = float(headers['X-RateLimit-Reset'])
        difference = datetime.datetime.utcfromtimestamp(reset) - epoch
#        reset_timer = difference.total_seconds()
        if rate_limit < 25:
            print "Rate limit approaching. " + str(rate_limit) + " requests remaining. Reset in " + str(difference) + "."
    except ValueError:
        pass
    if int(status) == 200:
#        json_output = json.loads(body)
#        print json.dumps(json_output, indent = 4)
        return body
    elif int(status) == 204:
        return
    elif int(status) == 429:
        print url
        print " *** Rate limit exceeded!"
        return None
    else:
        print url
        print " *** Returned Status: %s\n%s" % (status, body)
        return None


############################################################################
#### messaging and interaction functions


def parse_hipchat_message(message):
    """Take apart one hipchat message and convert it into an object."""
    msg = message['message']
    msg_type = message['type']
    date = message['date']
    msg_id = message['id']

    if msg_type == 'message':
        msg_from = message['from']['id']
    elif msg_type == 'notification':
        msg_from = find_user_by_name(message['from'])
        if msg_from == None:
            msg_from = ''
    else:
        msg_from = ''

    hm = HipchatMessage(msg_from, date, msg)
    hm.id = msg_id
    return hm


def find_user_by_name(name):
    """Given a name, look up the appropriate user."""
    for u in users:
        if users[u].name == name:
            return users[u]
    return None


def is_friend(user_id):
    """Given a user id, check to see if we're in the friend list."""
    for friend in friends:
        if friend.id == user_id:
            return True
    return False


def get_users():
    """Get a list of all Hipchat users."""
    url = '/v2/user'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    room_users = {}
    for j in json_output["items"]:
        room_users[j['id']] = HipchatUser(j['id'], j['name'], j['mention_name'])
    return room_users


def get_friends():
    """Get a list of 'friends' (admins).

    Friends are the participants of the command and control room.
    """
    my_friends = list_room_participants(control_room)
    return my_friends


def list_rooms():
    """Get a list of rooms in Hipchat."""
    url = '/v2/room'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = {}
    for j in json_output["items"]:
        l[j['id']] = j['name']
    return l


def list_room_participants(room_id):
    """Given a room_id, get a list of participants."""
    url = '/v2/room/' + str(room_id) + '/participant'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = []
    for j in json_output["items"]:
        l.append(users[j['id']])
    return l


def get_latest_message(room_id):
    """Get the newest message of the room."""
    url = '/v2/room/' + str(room_id) + '/history/latest?max-results=1'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = []
    for j in json_output["items"]:
        hm = parse_hipchat_message(j)
        hm.room = room_id
        l.append(hm)
    return l


def get_room_history(room_id):
    """Get the most recent messages for the room."""
    url = '/v2/room/' + str(room_id) + '/history/latest'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = []
    for j in json_output["items"]:
        hm = parse_hipchat_message(j)
        hm.room = room_id
        l.append(hm)
    return l


def notify_room(room_id, message):
    """Send a message to a room_id."""
    data = json.dumps({
        'message': message,
        'color': color,
        'message_format': 'text',
        'notify': True})
    url = '/v2/room/' + str(room_id) + '/notification'
    rest('post', url, data)

def notify_control(message):
    """Send a command to the control room."""
    notify_room(control_room, message)

def get_room_last_active(room_id):
    """Return the last active timestamp of the room."""
    url = '/v2/room/' + str(room_id) + '/statistics'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    try:
#        print "Last active ("+str(room_id)+"): " + str(json_output['last_active'])
        date = datetime.datetime.strptime(json_output['last_active'],
                            "%Y-%m-%dT%H:%M:%S+00:00")
        return date
    except ValueError:
        return datetime.date.min


def get_room_name(room_id):
    url = '/v2/room/' + str(room_id)
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    return json_output["name"]


rate_limit = 0

f = open('config.yml')
config_data = yaml.safe_load(f)
f.close()

base_url = config_data["base_url"]
token = config_data["token"]
working_dir = config_data["working_dir"]
temp_dir = config_data["temp_dir"]
control_room = config_data["control_room"]
auth = 'Bearer ' + token
color = config_data["notification_color"]
api_user = config_data["user"]

cmds = {
    "GET": _api_get,
#    "PUT": _api_put,
    "POST": _api_post,
#    "DELETE": _api_del
    }

users = get_users()

rooms = list_rooms()

api_user_id = find_user_by_name(api_user)

friends = get_friends()

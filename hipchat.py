
# import necessary modules

import sys
import traceback
import getopt
import json
import datetime
import dateutil
import threading
import time
import re

try:
    import requests
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

    def __init__(self, roomid):
        self.roomid = roomid
        self.update()
        self.lastmsg = None
        self.active = False
        self.check_interval = 10
        self.thread = None
        self.control_room = False
        if self.roomid == control_room:
            self.control_room = True
        self.response_list = {}

    def set_response_list(self, responses):
        self.response_list = responses

    def watch_room(self):
        self.active = True
        self.thread = threading.Thread(target=self.room_watcher)
        self.thread.daemon = True
        self.thread.start()
        notify_room(control_room, "Begun watch of room:" + str(self.roomid))

    def stop_watching(self):
        self.active = False
        notify_room(control_room, "Stopping watch of room:" + str(self.roomid))
        self.thread.join()

    def room_watcher(self):
        while self.active:
            time.sleep(self.check_interval)
            print "Checking messages in room: " + str(self.roomid)
            self.check_messages()

    def update(self):
        self.participants = list_room_participants(self.roomid)

    def publish_status(self):
        status = "Status of <botname>:\nIP: <IP address>\nSystems: <normal>"
        notify_room(self.roomid, status)

    def check_messages(self):
        if self.lastmsg == None:
            messages = get_latest_message(self.roomid)
            self.lastmsg = messages[0].date
            return
        messages = get_room_history(self.roomid)
        response = ""
        for one_message in messages:
            if one_message.fromid == api_user_id:
                continue
            new_date = self.lastmsg
            if self.lastmsg > one_message.date:
                pass
            elif new_date < one_message.date:
                new_date = max(one_message.date, new_date)
                result = ""
                result = self.process_one_message(one_message)
                print str(one_message.date) + " : " + str(one_message)
                if result == "":
                    print "\tResult: ignored"
                else:
                    print "\tResult: " + result
                    response = result
        if response != "":
            notify_room(self.roomid, response)
        self.lastmsg = new_date

    def process_one_message(self, message):
        word_list = re.split('\W+',message.msg.lower())
        for needle in self.response_list:
            if needle.lower() in word_list:
                response = self.response_list[needle](needle, message)
                return response
        return ""


class HipchatMessage:

    def __init__(self, fromid, date, msg):
        self.fromid = fromid
        # sample date to parse: 2015-04-24T22:10:44.146716+00:00
        self.date = datetime.datetime.strptime(date,
                            "%Y-%m-%dT%H:%M:%S.%f+00:00")
        self.msg = msg
        self.id = ''
        self.room = 0
        
    def __str__(self):
        return self.msg
        
    def is_control(self):
        if self.room == control_room:
            return True
        return False
        
    def is_friend(self):
        if fromid in friends:
            return True
        return False


class HipchatUser:

    def __init__(self, id, name, mentionname):
        self.id = id
        self.name = name
        self.mentionname = mentionname

    def __str__(self):
        return self.name


def _api_get(url, data=None):
    url, data = url, data
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json',
                          'Authorization': auth}
    response = requests.get(url, headers=requisite_headers)
    return response.status_code, response.text


def _api_put(url, data):
    url, name, passwd = url, user, token
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json'}
    auth = (name, passwd)
    response = requests.put(url, headers=requisite_headers,
                                auth=auth, params=data)
    return response.status_code, response.text


def _api_post(url, data):
    url, data = url, data
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json',
                          'Authorization': auth}
    response = requests.post(url, headers=requisite_headers, data=data)
    return response.status_code, response.text


def _api_del(argv):
    url, name, passwd = argv[0], argv[1], argv[2]
    requisite_headers = {'Accept': 'application/json',
                          'Content-Type': 'application/json'}
    auth = (name, passwd)
    response = requests.delete(url, headers=requisite_headers, auth=auth)
    return response.status_code, response.text

#    def load_file(fname):
#        with open(fname) as f:
#            return f.read()


def rest(req, url, data=None):
    url = base_url + url
#        print url
    if 'HTTPS' not in url.upper():
        print ("Secure connection required: HTTP not valid, "
                    "please use HTTPS or https")
        rest_usage()
    cmd = req.upper()
    if cmd not in cmds.keys():
        rest_usage()
    status, body = cmds[cmd](url, data)
    if int(status) == 200:
        json_output = json.loads(body)
#            print json.dumps(json_output, indent = 4)
        return body
    else:
        print "Status: %s\n%s" % (status, body)
        print


############################################################################
#### messaging and interaction functions


def parse_hipchat_message(message):
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
    """Given a name, look up the appropriate user
    """
    global users
    for u in users:
        if users[u].name == name:
            return users[u]
    return None


def is_friend(id):
    """Given a user id, check to see if we're in the friend list
    """
    global friends
    for f in friends:
        if f.id == id:
            return True
    return False


def get_users():
    """ Get a list of all Hipchat users"""
    url = '/v2/user'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    users = {}
    for j in json_output["items"]:
        users[j['id']] = HipchatUser(j['id'], j['name'], j['mention_name'])
    return users


def get_friends():
    """ Get a list of 'friends', meaning the participants
    of the command and control room. These people are
    functionally admins.
    """
    friends = list_room_participants(control_room)
    return friends


def list_rooms():
    url = '/v2/room'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = {}
    for j in json_output["items"]:
        l[j['id']] = j['name']
    return l


def list_room_participants(room_id):
    url = '/v2/room/' + str(room_id) + '/participant'
    body = rest('get', url, data=None)
    json_output = json.loads(body)
    l = []
    for j in json_output["items"]:
        l.append(users[j['id']])
    return l


def get_latest_message(room_id):
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
    data = json.dumps({
        'message': message,
        'color': color,
        'message_format': 'text',
        'notify': True})
    url = '/v2/room/' + str(room_id) + '/notification'
    rest('post', url, data)


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
    "PUT": _api_put,
    "POST": _api_post,
    "DELETE": _api_del}

users = get_users()

api_user_id = find_user_by_name(api_user)

friends = get_friends()

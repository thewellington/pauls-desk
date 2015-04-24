#!/usr/bin/env python
#
#

# import necessary modules

import sys
import traceback
import getopt
import json

try:
  import requests
except ImportError:
  sys.stderr.write("You do not have the 'requests' module installed.  Please see http://docs.python-requests.org/en/latest/ for more information.")
  exit(1)

try:
  import yaml
except ImportError:
  sys.stderr.write("You do not have the 'yaml' module installed.  Please see http://pyyaml.org/wiki/PyYAMLDocumentation for more information.")
  exit(1)


# get configuration from yaml and populate variables

f = open ('config.yml')
config_data = yaml.safe_load(f)
f.close()

base_url = config_data["base_url"]
token = config_data["token"]
working_dir = config_data["working_dir"]
temp_dir = config_data["temp_dir"]

auth = 'Bearer ' + token


############################################################################ 
#### begin api interactions


def _api_get(url, data=None):
    url, data = url, data
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json',
                          'Authorization' : auth
    }
    
    response =  requests.get(url, headers=requisite_headers)
    
    return response.status_code, response.text


def _api_put(url, data):
    url, name, passwd = url, user, token
    
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
 
#     if len(argv) > 3:
#         data = load_file(argv[3])
#     else:
#         data = None

    response =  requests.put(url, headers=requisite_headers, auth=auth, params=data)

    return response.status_code, response.text
    

def _api_post(url, data):
    url, data = url, data
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json',
                          'Authorization' : auth
    }
 
    response =  requests.post(url, headers=requisite_headers, data=data)
    
    return response.status_code, response.text


def _api_del(argv):
    url, name, passwd = argv[0], argv[1], argv[2]
    
    requisite_headers = { 'Accept' : 'application/json',
                          'Content-Type' : 'application/json'
    }
    auth = (name, passwd) 
    
    response =  requests.delete(url, headers=requisite_headers, auth=auth)
    
    return response.status_code, response.text


def rest_usage():
    print "usage: rest [put|get|post|delete] url name passwd"
    sys.exit(-1)

cmds = {
    "GET": _api_get, 
    "PUT": _api_put, 
    "POST": _api_post,
    "DELETE": _api_del
    }

def load_file(fname):
  with open(fname) as f:
    return f.read()

def rest(req, url, data=None):

#     if len(argv) < 4:
#         rest_usage()
    print url
    
    if 'HTTPS' not in url.upper():
        print "Secure connection required: HTTP not valid, please use HTTPS or https"
        rest_usage()       
        
    cmd = req.upper()
    if cmd not in cmds.keys():
        rest_usage()

    status,body=cmds[cmd](url, data)
    print
    if int(status) == 200:
        json_output = json.loads(body)
        print json.dumps(json_output, indent = 4)        
        return body
    else:
        print "Status: %s\n%s" % (status, body)
        print
        
############################################################################ 
#### begin custom functions

def list_rooms():
  url = base_url+'/v2/room'
  body = rest('get', url, data=None)
  json_output = json.loads(body)
  
  l = []
#   for j in json_output:
#     l.append(j.get('id'))
    
  return l

def list_room_participants(room_id):
  url = base_url+'/v2/room/'+room_id+'/participant'
  body = rest('get', url, data=None)
  json_output = json.loads(body)
  
  l = []
#   for j in json_output:
#     l.append(j.get('items'))
    
  return l

def message_room(room_id):
  data = json.dumps({
        'message': 'this is a test',
        'color': 'yellow',
        'message_format': 'html',
        'notify' : False})
  url = base_url+'/v2/room/'+room_id+'/message'
  rest('post', url, data)
  






#       
# 
# def get_exclusions():
#   exclusions = []
#   f = open(control_dir+'/exclusions-final.conf', 'r')
#   for line in f:
#     exclusions.append(line.split("#",1)[0].rstrip())
#     
#   exclusions = filter(None, exclusions)  
#   
#   #encode exclusions in unicode
#   unicode_exclusions = [unicode(i) for i in exclusions]
#   
#   return unicode_exclusions
#   
# 
# def suspend_configurations():
#   configurations = set(get_configurations())
#   exclusions = set(get_exclusions())
#   suspends = list(configurations - exclusions)
#   
#   data = {'runstate' : 'suspended'}
# 
#   for i in suspends:
#     print i
#     rest('put', base_url+'/configurations/2156312?runstate=suspended', user, token, data=data)


  
############################################################################ 
#### begin interface items


def usage(exitcode):

  usage="""
  
  
##########################    Welcome to Skynet    #########################

  skynet [--help] [--action=<action-name>]

OPTIONS:
  --help, -h
    prints this document
    
  --action=<action-name>, -a <action-name>
    Take an action

ACTIONS:
  'suspend' will suspend configurations that are not on the exclusions list.
  
EXAMPLES:
  skynet -a suspend 

############################################################################ 


  
"""

  try:
    exitcode
  except NameError:
    print usage
    sys.exit(-1)
  else:
    print usage
    sys.exit(exitcode)

 
# argument parser
def ui(argv):
  
# define variables to be used by getopts and sent them to null
  action = ''
  scope = ''
  
#  print 'ARGV     :', sys.argv[1:]
  
  try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'a:hs:t', ['help',
                                                          'action=',
                                                          'scope=',
                                                          ])
                                            
  except getopt.GetoptError:
    usage()
    sys.exit(2)


#  print 'OPTIONS    :', options

  for opt, arg in options:
    if opt in ('-h', '--help'):
      usage(2)
      sys.exit()

    elif opt in ( '-a', '--action' ):
      action = arg
      if action == 'list-rooms':
        list_rooms()
      elif action == 'room-participants':
        list_room_participants('564688')
      elif action == 'message-room':
        message_room('1452085')
      elif action != 'suspend':
        usage(2)
      
    elif opt in ( '-s', '--scope' ):
      scope = arg
      usage(3)

    elif opt in ( '-t' ):
      print 'TEST ENVIRONMENT'
    
#   print 'ACTION   :', action
#   print 'SCOPE      :', scope
#   print 'REMAINING  :', remainder




 
# call main
if __name__=='__main__':

  ui(sys.argv[1:]) 

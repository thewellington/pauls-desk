#!/usr/bin/env python

import json
import urllib
import urllib2

control_room = "1452085"
token = "wUsJsycnQajhQSQnKlaN7T33jAte21GLFxfaWCXh"
baseurl = "https://api.hipchat.com"

headers = {"authorization":"Bearer wUsJsycnQajhQSQnKlaN7T33jAte21GLFxfaWCXh", "content-type":"application/json"}

data = json.dumps({
  'message': 'this is a test',
  'color': 'yellow',
  'message_format': 'html',
  'notify': False})
  

def api_get( obj ):
  url = baseurl + obj
  request = urllib2.Request(url)
  response = urllib2.urlopen(request)

  print response.read()

def api_post( obj, data, headers ):
  url = baseurl + obj + "/"
  request = urllib2.Request(url=url, data=data, headers=headers,)
  response = urllib2.urlopen(request)
  
  print response
  
  
#def main():

if __name__ == '__main__':
#  api_get( "/v2/room?auth_token=wUsJsycnQajhQSQnKlaN7T33jAte21GLFxfaWCXh" )
  api_post( "/v2/room/" + control_room, data, headers )

#! /usr/bin/env python
""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.


A simple script demonstrating how to add new users and delete them.
Note that this isn't a great script to run on your production system,
but it will create a user unlikely to conflict with the ones you have.
This is more of sample code than anything else.

"""

import requests, logging, json
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
import time
session = requests.Session()
debug = False
verbose = False
section_name = "user"

config = EdgeGridConfig({"verbose":False},section_name)

if hasattr(config, "debug") and config.debug:
  debug = True

if hasattr(config, "verbose") and config.verbose:
  verbose = True

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

if hasattr(config, 'headers'):
	session.headers.update(config.headers)

baseurl = '%s://%s/' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

def getUsers():
  print "Getting Users"
  user_result = httpCaller.getResult('/user-admin/v1/accounts/B-C-1FRYVMN')
  for user in user_result:
    print "\t" + user["username"]
  print

def createUserRequest():
	ts = time.time()
	username = "kirsten.%s.hunter@akamai.com" % ts
    	user_obj = {"firstName":"Kirsten","lastName":"Hunter","email":username,"phone":"(831) 588-7563","timezone":"GMT","roleAssignments":[{"groupId":"41241","roleId":14}],"authPolicies":[]}

	print "Creating user"
	user_post_result = httpCaller.postResult('/user-admin/v1/users', json.dumps(user_obj))
	print "\tUser created\n"
	return user_post_result["contactId"]

def deleteUserRequest(contactid):
  print "Deleting user %s" % contactid
  endpoint_result = httpCaller.deleteResult('/user-admin/v1/users/%s' % contactid)
  print "\tUser deleted\n"

def deleteUserRoleRequest(contactid):
  print "Updating user to remove role %s" % contactid
  user_obj = {"roleAssignments":[{"groupId":"41241","roleId":None}]}

  endpoint_result = httpCaller.putResult('/user-admin/v1/users/%s' % contactid, json.dumps(user_obj))
  endpoint_result = httpCaller.deleteResult('/user-admin/v1/users/%s' % contactid)
  print "\tUser role removed\n"

if __name__ == "__main__":

  getUsers()
  # First, create the user then delete them 
  contactid = createUserRequest()
  getUsers()
  deleteUserRequest(contactid)
  getUsers()
 
  # Now, create the user and remove their role (which deletes them)
  contactid = createUserRequest()
  deleteUserRoleRequest(contactid)
  deleteUserRequest(contactid)
  getUsers()

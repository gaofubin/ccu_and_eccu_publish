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

Sample client for network-lists
In order to "create" a new list, you'll want to 
remove the # at the beginning of the "createNetworkList" call
and update the IP addresses to be appropriate for your needs.
"""



import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False
verbose = False
section_name = "networklists"

# If all parameters are set already, use them.  Otherwise
# use the config
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


def getNetworkLists():
	print
	print "Requesting the list of network lists"

	events_result = httpCaller.getResult('/network-list/v1/network_lists')
	return events_result

def createNetworkList(name,ips):
	print "Creating a network list %s for ip addresses %s" % (name, json.dumps(ips))
	headers = {'Content-Type': 'application/json'}
	path = "/network-list/v1/network_lists"
	data_obj = {
		"name" : name,
		"type" : "IP",
		"list" : ips
	}
	
	httpCaller.postResult(urljoin(baseurl,path), json.dumps(data_obj))

if __name__ == "__main__":
	Id = {}
	lists = getNetworkLists()["network_lists"]
	def mapper(x):
		print str(x["numEntries"]) + ", " + x["name"]
	map(mapper, lists)
	#createNetworkList("test",["1.2.3.4"])


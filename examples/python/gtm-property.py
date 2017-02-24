#! /usr/bin/env python
# Very basic script template.  Use this to build new
# examples for use in the api-kickstart repository
#
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
"""

import requests, logging, json
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib
session = requests.Session()
debug = False
verbose = False
section_name = "gtm"

config = EdgeGridConfig({"verbose":debug},section_name)

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

# Set the baseurl based on config.host
baseurl = '%s://%s/' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

if __name__ == "__main__":
	# Set these two to the appropriate values for your system
	domainname = "akamaiapibootcamp.com.akadns.net"
	propertyname = "origin"

	endpoint = "/config-gtm/v1/domains/%s/properties/%s" % (domainname, propertyname)
	# First, get the existing property
	property_object = httpCaller.getResult(endpoint)

	# Remove the pieces that aren't settable
	del property_object["links"]
	del property_object["lastModified"]

	# Change the weight for first and second datacenters
	property_object["trafficTargets"][0]["weight"] = 1
	property_object["trafficTargets"][0]["name"] = "mediatemple"

	property_object["trafficTargets"][1]["weight"] = 1 
	property_object["trafficTargets"][1]["name"] = "digitalocean"
	# Add a liveness test
	property_object["livenessTests"] = [ 
		{
     			  "responseString": None, 
     			  "testObject": "/Resume.html",
      			"disableNonstandardPortWarning": False, 
      			"name": "Test", 
      			"httpError5xx": True, 
      			"sslClientPrivateKey": None, 
      			"testObjectUsername": "khunter", 
      			"httpError4xx": True, 
      			"httpError3xx": True, 
      			"hostHeader": None, 
      			"testObjectPassword": None, 
      			"testTimeout": 25.0, 
      			"sslClientCertificate": None, 
      			"requestString": None, 
      			"testObjectPort": 80, 
      			"testInterval": 60, 
      			"testObjectProtocol": "HTTP"
		} ]
  
	result = httpCaller.putResult(endpoint, json.dumps(property_object))
	print ("Success!")

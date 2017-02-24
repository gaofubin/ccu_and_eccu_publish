#! /usr/bin/env python
# Very basic script demonstrating diagnostic tools functionality
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
import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib
session = requests.Session()
debug = False
verbose = False
section_name = "default"

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({},section_name)

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

baseurl = '%s://%s' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug,verbose, baseurl)

# functions
def purge_by_urls():
    data={
       "objects" : [
        "http://ninjatw.patch.uqsoft.com/cdntest/"
       ]
    }
    result = httpCaller.postResult('/ccu/v3/delete/url/production', json.dumps(data, sort_keys=False, indent=4))
    print json.dumps(result, sort_keys=True, indent=4)

if __name__ == "__main__":
    purge_by_urls()









'''
# Request locations that support the diagnostic-tools
print
print ("Requesting locations that support the diagnostic-tools API.\n")

location_result = httpCaller.getResult('/diagnostic-tools/v1/locations')

# Select a random location to host our request
location_count = len(location_result['locations'])

print("There are {} locations that can run dig in the Akamai Network".format(location_count))
rand_location = randint(0, location_count-1)
location = location_result['locations'][rand_location]
print ("We will make our call from " + location + "\n")

# Request the dig request the {OPEN} Developer Site IP informantion
dig_parameters = { "hostname":"ninjatw.patch.uqsoft.com", "location":location, "queryType":"A" }
#dig_parameters = { "hostname":"developer.akamai.com", "location":location, "queryType":"A" }
dig_result = httpCaller.getResult("/diagnostic-tools/v1/dig",dig_parameters)
#dig_result = httpCaller.getResult("/ccu/v3/delete/url/production",dig_parameters)

# Display the results from dig
print (dig_result['dig']['result'])
'''

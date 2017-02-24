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
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False
verbose = False
section_name = "default"

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
	# If you're just doing a simple GET the call is very simple
	# endpoint_result = httpCaller.getResult("ENDPOINT")
	# result_value = endpoint_result["VARIABLE")

	# Add parameters
	request_parameters = { "value1":"foo","value2":"bar" }
	endpoint_result = httpCaller.getResult("ENDPOINT",request_parameters)
	# result_value = endpoint_result["VARIABLE")

	# POST example
	#     	sample_obj = { "roleAssignments": [ { "roleId": 14, "groupId": 41241 } ], 
    	#		"firstName": "Kirsten", 
    	#		"phone": "8315887563", 
    	#		"lastName": "Hunter", 
    	#		"email": "kirsten.hunter@akamai.com"
   	#	}
	# sample_post_result = httpCaller.postResult('/user-admin/v1/users', json.dumps(user_obj))

	print "Waiting for some fabulous code here!"

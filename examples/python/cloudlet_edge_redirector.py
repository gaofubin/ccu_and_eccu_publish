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
section_name = "cloudlet"

# Let's set up exactly which policy and version we want to use
policy = "15927"
version = "CREATE" # CREATE OR LATEST OR SPECIFIC NUMBER
filename = "rules.json"

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
	# Get the list of cloudlets to pick the one we want to use

	if version == "CREATE":
		new_version_info = {
				"description":"Adding a new version for match rules",
				"matchRuleFormat":"1.0",
				"matchRules": []
		}
		create_path = "/cloudlets/api/v2/policies/%s/versions" % policy
		create_result = httpCaller.postResult(create_path, 
							json.dumps(new_version_info))

	if version == "CREATE" or version == "LATEST":
		version_path = "/cloudlets/api/v2/policies/%s/versions" % policy
		version_result = httpCaller.getResult(version_path)
		version = version_result[0]["version"]

	# Now we know which version (and we've set the policy)

	# Open the JSON filename with mappings
	with open(filename) as data_file:
		data = json.load(data_file)

	for rule in data:
		rule_path = "/cloudlets/api/v2/policies/%s/versions/%s/rules" % (policy, version)
		rule_result = httpCaller.postResult(rule_path, json.dumps(rule))
		print rule_result

	# Activate the new version if you like
	activation_path = "/cloudlets/api/v2/policies/%s/versions/%s/activations" % (policy, version)
	activation_obj = {
		"network":"production"
	}
	activation_result = httpCaller.postResult(activation_path, json.dumps(activation_obj))
		


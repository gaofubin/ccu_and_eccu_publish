#! /usr/bin/python

""" Sample client for VP API
Licensed under Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Author: Ian Cass <icass@akamai.com>

For this to work, you need an activated site configuration that has
Visitor Prioritization enabled on it. Please make sure that the
configuration exists in the default group for the api user.

You then need to create one or more VP policies and ensure that you 
can activate using Luna.

Also, make sure that your API user has read/write permissions for 
Visitor Prioritization API

If you want to pass parameters, you can do so as follows.  

activate-vp.py --config=<config> --policy=<policy> --version=<version> --network=<network>

"""

import time
import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import pprint

session = requests.Session()
debug = False

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({"configuration":"Visitor Prioritization",
			 "policy":"store_poc",
			 "version":"4",
			 "network":"staging"},
			"default")


# Enable debugging for the requests module
if debug:
	print "Setting up debugging"
	import httplib as http_client
	http_client.HTTPConnection.debuglevel = 1
	logging.basicConfig()
	logging.getLogger().setLevel(logging.DEBUG)
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True


# Set the config options
session.auth = EdgeGridAuth(
	client_token=config.client_token,
	client_secret=config.client_secret,
	access_token=config.access_token
)


session.headers.update({"x-testheader": "testdata"})

baseurl = "%s://%s/" % ("https", config.host)

def getResult(endpoint, parameters=None):
	if parameters:
		parameter_string = urllib.urlencode(parameters)
		path = "".join([endpoint + "?",parameter_string])
	else:
		path = endpoint
		endpoint_result = session.get(urljoin(baseurl,path))
	if debug:
		print endpoint_result.json()
	return endpoint_result.json()

def getPostResult(endpoint, parameters):
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","Accept":"application/json"}
        data_string = urllib.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        result = session.post(urljoin(baseurl,endpoint),data=data_string, headers=headers)
	if debug:
		print result.text
        obj = json.loads(result.text)
        return obj

def getAllActivations():
	return getResult("/config-visitor-prioritization-data/api/v1/common/activation?historyOnly=false");

def getVPActivation():
	activations = getAllActivations()
	for activation in activations:
		if activation["name"] == config.configuration:
			return activation
	raise RuntimeError("Can't find the Activation record")

def getActivation(v):
	print
	print "Getting Activation record for version " + v
	vpactivation = getVPActivation()
	for policy in vpactivation["policies"]:
		if policy["policyName"] == config.policy:
			for version in policy["versions"]:
				if version["version"] == v:
					activation = {"fileId":vpactivation["fileId"], "assetId":vpactivation["assetId"], "policyVersionId":version["policyVersionId"]}
					if debug:
						pprint.pprint(activation)
					return activation
	raise RuntimeError("No Activation records found with the requested version")

def getPolicies():
	print
	print "Requesting policies"

        path = "/config-visitor-prioritization-data/api/v1/policymanager?command=getAllPolicyInfoMaps"
        parameters = { "query": {"policyManagerRequest": { "command": "getPolicyInfoMapUsingACGIDs", "getPolicyInfoMapUsingACGIDs":{} } } }
	return getPostResult(path, parameters)

def activatePolicy(activation):
	print "Setting policy"
	pprint.pprint(activation)
        path = "/config-visitor-prioritization-data/api/v1/policymanager"
	parameters = { "query": { "policyManagerRequest": { "command": "activate", "activate": { "tapiocaIDs": [ activation["policyVersionId"] ], "arlId": str(activation["fileId"]), "assetId": str(activation["assetId"]), "network": NETWORK } } } }
	return getPostResult(path, parameters)

if __name__ == "__main__":
	print "Starting..."
	print getPolicies()
	activation = getActivation(config.version)
	result = activatePolicy(activation)
	pprint.pprint(result)

		

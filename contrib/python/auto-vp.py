#! /usr/bin/python

""" Sample applicaton for automatic Visitor Prioritization activation
Licensed under Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Author: Ian Cass <icass@akamai.com>

This application will poll the alerts api and when it finds a high
traffic alert, it will activate the VP policy version that's been
configured for sending users the the waiting room. When it see's a
low traffic alert, it will activate another policy version that's
been configured to send end users direct to origin.

For this to work, you need an activated site configuration that has
Visitor Prioritization enabled on it. Please make sure that the
configuration exists in the default group for the api user.
Also, make sure that your API user has read/write permissions for
Visitor Prioritization API

You then need to create two VP policies, one for sending a percentage
to waiting room and one for sending all to origin. 

You then need to create an alert for High Traffic that will fire
when the site traffic exceeds a comfortable level. Ideally this alert
would only fire for traffic that needed to be sent to waiting room, but
you can only specify a CPCode not a url, so you could assign a CPCode
to a url using the site configuration. Make sure to disable the email
alert.

And finally, you need to create a Low Traffic alert that's somewhat
below the value that you set for High Traffic. This is acting as a low
watermark and will trigger the waiting room to switch off. Once again
use the same CPCode and make sure to turn off emails for this alert

Note, this application is very much BETA and work in progress. This 
is not production ready and has not been thoroughly tested. You are
on your own with this code. You need to use it purely as an example
and as a starting point for your own application.

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
debug = True

CONFIGNAME = "CONFIG_NAME"      # This is the name of your site configuration
VPNAME = "POLICY_NAME"          # This is the name of your policy
NETWORK = "staging"             # staging or production
LOWVER = "1"			# The version of your VP Policy for low traffic
HIGHVER = "2"			# The version of your VP Policy for high traffic


# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({},"default")
if hasattr(config, 'verbose'):
	debug = config.verbose

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


session.headers.update({'x-testheader': 'testdata'})

baseurl = '%s://%s/' % ('https', config.host)

def getResult(endpoint, parameters=None):
        if parameters:
                parameter_string = urllib.urlencode(parameters)
                path = "".join([endpoint + "?",parameter_string])
        else:
                path = endpoint
                endpoint_result = session.get(urljoin(baseurl,path))
        return endpoint_result.json()

def getPostResult(endpoint, parameters):
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8","Accept":"application/json"}
        data_string = urllib.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        result = session.post(urljoin(baseurl,endpoint),data=data_string, headers=headers)
        obj = json.loads(result.text)
        return obj

def getAllActivations():
        return getResult("/config-visitor-prioritization-data/api/v1/common/activation?historyOnly=false");

def getVPActivation():
        activations = getAllActivations()
        for activation in activations:
                if activation["name"] == CONFIGNAME:
                        return activation
        raise RuntimeError("Can't find the Activation record")

def getActivation(v):
        print
        print "Getting Activation record for version " + v
        vpactivation = getVPActivation()
        for policy in vpactivation["policies"]:
                if policy["policyName"] == VPNAME:
                        for version in policy["versions"]:
                                if version["version"] == v:
                                        activation = {"fileId":vpactivation["fileId"], "assetId":vpactivation["assetId"], "policyVersionId":version["policyVersionId"]}
                                        if debug:
                                                pprint.pprint(activation)
                                        return activation
        raise RuntimeError("No Activation records found with the requested version")

def getAlerts():
        print
        print "Checking alerts"
	alerts = getResult('/alerts/v1/portal-user?status=active&cpCodes=353651')
        return alerts['alertList']

def activatePolicy(activation):
        print "Setting policy"
        path = "/config-visitor-prioritization-data/api/v1/policymanager"
        parameters = { "query": { "policyManagerRequest": { "command": "activate", "activate": { "tapiocaIDs": [ activation["policyVersionId"] ], "arlId": str(activation["fileId"]), "assetId": str(activation["assetId"]), "network": NETWORK } } } }
        return getPostResult(path, parameters)

if __name__ == "__main__":
	print "Starting..."
	highActivation = getActivation(HIGHVER)
	loActivation = getActivation(LOWVER)

	ALERTTYPES = { 'High Traffic -- Content Delivery':{'state':1, 'activation':highActivation}, 'Low Traffic -- Content Delivery':{'state':2,'activation':loActivation}}

	currentState = 0
	cont = True
	while (cont):
		alerts = getAlerts()
		if alerts:
			for alert in alerts['alerts']:
				alertType = ALERTTYPES[alert['type']]
				if alertType['state'] != currentState:
					print alert['type']
					currentState = alertType['state']
					pprint.pprint(activatePolicy(alertType['activation']))
		print "Sleeping zzz"
		time.sleep(30)

		

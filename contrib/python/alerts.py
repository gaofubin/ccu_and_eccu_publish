#! /usr/bin/python

""" Sample client for Alerts API
Licensed under Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Author: Ian Cass <icass@akamai.com>

This will list the alerts that are available for the given CPCode

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

CPCODE = "123456"	# Your CPCODE

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({},"default")
if hasattr(config, "verbose"):
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


session.headers.update({"x-testheader": "testdata"})

baseurl = "%s://%s/" % ("https", config.host)

def getResult(endpoint, parameters=None):
	if parameters:
		parameter_string = urllib.urlencode(parameters)
		path = "".join([endpoint + "?",parameter_string])
	else:
		path = endpoint
		endpoint_result = session.get(urljoin(baseurl,path))
	return endpoint_result.json()

def getAlerts():
        print
        print "Checking alerts"
	alerts = getResult("/alerts/v1/portal-user?status=active&cpCodes=" + CPCODE)
        return alerts["alertList"]

if __name__ == "__main__":
	print "Starting..."
	alerts = getAlerts()
	pprint.pprint(alerts)

		

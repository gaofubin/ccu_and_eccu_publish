#!/usr/bin/python

""" Sample client for CCU

Licensed under Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

Author: Kelly Kane <kelly.kane@openx.com>

Note that in order for this to work you need to provision credentials
specifically for CCU - you cannot extend existing credentials to add
CCU as it's managed under "CCU" in the API credential system.

Configure->Organization->Manage APIs
Select "CCU APIs"
Create client collections/clients
Add authorization

Put the credentials in ~/.edgerc like:

[ccu]
host = akab-blah-blah.purge.akamaiapis.net/
client_token = akab-blah-blah
client_secret = longstring+sosecret=
access_token = akab-getthis-fromtheportal

Usage:
   ccu.py --cpcode #####
   ccu.py --file file.txt
   ccu.py --check UUID-from-prior-run

"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from urlparse import urljoin
import urllib
import os, sys
import argparse
import ConfigParser

#Snag some arguments, namely invalidate by CPCode or URL/ARLs in a file.
parser = argparse.ArgumentParser(
								formatter_class=argparse.RawDescriptionHelpFormatter,
								description="""
Implements the Akamai Content Control Utility

Example Commands:
   ccu.py --cpcode #####
   ccu.py --file file.txt
   ccu.py --check UUID-from-prior-run
   ccu.py --debug --network staging --config_file /etc/edgerc --config_section globalcreds --cpcode 0123456
""")

parser.add_argument('--config_file', default='~/.edgerc', type=str, metavar='FILENAME',
					help='Path to your edgerc config file.')
parser.add_argument('--debug', action='store_true',
					help='Way too much information.')
parser.add_argument('--network', default="production", choices=['production','staging'],
					help='Act on the production or staging network.')
parser.add_argument('--config_section', default='ccu', type=str,
					help='Which section of the edgerc file to use? [ccu] or [myname] for example.')

#Can't invalidate by CPCode and URL list in a single call.
args_exclusive = parser.add_mutually_exclusive_group(required=True)
args_exclusive.add_argument('--cpcode', type=int, 
							help="CPCode to purge.")
args_exclusive.add_argument('--file', type=str, 
							help="URL file to load. One URL per line.")
args_exclusive.add_argument('--check', type=str, metavar='PURGE_ID', 
							help="Check a running invalidate request.")

args = parser.parse_args()

# Build the JSON blob to send to Akamai. 
# It MUST be a list, even if it's just the one.
def BuildCPCodeReqBody(network, cpcode):
	req = {
		"objects" : [ cpcode ],
		"action" : "invalidate",
		"type" : "cpcode",
		"domain" : network
		}
	return json.dumps(req)

def BuildURLReqBody(network, urlfile):
	urlfile = os.path.expanduser(urlfile)
	if debug: print "DEBUG: urlfile", urlfile
	
	if os.path.isfile(urlfile):
		with open(urlfile, 'r') as f:
			urls = f.read().splitlines()
		f.close()
		
		#Snag a trailing newline / newline only lines / empty lines
		urls = [ x for x in urls if (x != "\n" and x != '')]
		
		if debug: print "URL list:", urls
	else:
		print "Missing configuration file.  Run python gen_creds.py to get your credentials file set up once you've provisioned credentials in LUNA."
		exit()

	req = {
		"objects" : urls,
		"action" : "invalidate",
		"type" : "arl",
		"domain" : network
		}
		
	if debug: print json.dumps(req)
	return json.dumps(req)

#Load your edgerc file, parse it out into the format EdgeGridAuth likes.	
def AkamaiEdgeGridConfig_Setup(config_file, section):
	config_file = os.path.expanduser(config_file)	
	if debug: print "DEBUG: config_file", config_file
	
	#Currently unused.
	required_options = ['client_token','client_secret','host','access_token']
	EdgeGridConfig = {}

	if os.path.isfile(config_file):
		config = ConfigParser.ConfigParser()
		config.readfp(open(config_file))
		for key, value in config.items(section):
			# ConfigParser lowercases magically
			EdgeGridConfig[key] = value
	else:
		print "Missing configuration file.  Run python gen_creds.py to get your credentials file set up once you've provisioned credentials in LUNA."
		exit()

	EdgeGridConfig['host'] = '%s://%s' % ('https', EdgeGridConfig['host'])
	
	if debug: print EdgeGridConfig
	return EdgeGridConfig

#Setup a EdgeGrid Session using the EdgeGridConfig previously loaded.
def AkamaiEdgeGridSession_Setup(AkamaiEdgeGridConfig):
	session = requests.Session()
	
	session.auth = EdgeGridAuth(
				client_token=AkamaiEdgeGridConfig['client_token'],
				client_secret=AkamaiEdgeGridConfig['client_secret'],
				access_token=AkamaiEdgeGridConfig['access_token']
	)
	
	return session

#Actually call akamai and return the result.
def DoInvalidateRequest(session, url, req):
	itsjson = {'content-type': 'application/json'}
	
	result = session.post(url,data=req,headers=itsjson)
	if (result.status_code == 201):
		purge_id_url = result.headers['content-location'].split('/')
		purge_id = purge_id_url[-1]
		return purge_id
	else:
		print "Request failed:", result.status_code
		return False

def DoCheckStatus(session, url, purge_id):
	url = url + purge_id
	
	result = session.get(url)

	if (result.status_code == 200):
		#json.load the text before json.dumping it. Using seemingly saner methods wasn't working.
		print json.dumps(json.loads(result.text),sort_keys=True, indent=4, separators=(',', ': '))

		return True
	else:
		print "Request failed:", result.status_code
		return False
	
# Enable debugging for the requests module
debug = args.debug
if debug:
	import httplib as http_client
	http_client.HTTPConnection.debuglevel = 1
	logging.basicConfig()
	logging.getLogger().setLevel(logging.DEBUG)
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True
else:
	requests.packages.urllib3.disable_warnings()

# Set the config options
AkamaiEdgeGridConfig = AkamaiEdgeGridConfig_Setup(args.config_file, args.config_section)
AkamaiEdgeGridSession = AkamaiEdgeGridSession_Setup(AkamaiEdgeGridConfig)

#Endpoints!
queue_url = AkamaiEdgeGridConfig['host'] + 'ccu/v2/queues/default'
check_url = AkamaiEdgeGridConfig['host'] + 'ccu/v2/purges/'

if (args.cpcode):
	print 'Invalidate by CPCode:', args.cpcode, '\n'
	
	req = BuildCPCodeReqBody(args.network,args.cpcode)
	if debug: print req
	
	purge_id = DoInvalidateRequest(AkamaiEdgeGridSession, queue_url, req)
	if purge_id:
		print "Request successful to invalidate cpcode", args.cpcode
		print "Check status with", sys.argv[0], "--check", purge_id
	else:
		print "Request failed."
		
elif (args.file):
	print 'Invalidate by URLs in file:', args.file
	req = BuildURLReqBody(args.network, args.file)
	purge_id = DoInvalidateRequest(AkamaiEdgeGridSession, queue_url, req)

	if purge_id:
		print "Request successful to invalidate urls in file", args.file
		print "Check status with", sys.argv[0], "--check", purge_id
	else:
		print "Request failed."

elif (args.check):
	print 'Checking status of purge:', args.check
	DoCheckStatus(AkamaiEdgeGridSession, check_url, args.check)


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

Sample client 
In order to use this papi client you will need to have access turned
on for your account.  Send the contract IDs you want activated in a 
request to open-developer@akamai.com.

This script pulls the contract groups, properties for that group, and
products for that contract.

Please send any comments, questions or ideas to open-developer@akamai.com

Thanks!
The Akamai Developer Relations Team

"""

import requests, logging, json, random, sys, re
from http_calls import EdgeGridHttpCaller
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
from subprocess import call
import os
session = requests.Session()
debug = False
verbose = False
section_name = "papi"

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


def getGroup():
	"""
	Request the list of groups for the account.  Print out
	how many groups there are, then use the first group where
	the test property lives.

	"""
	print
	print "Requesting the list of groups for this account"

	groups_result = httpCaller.getResult('/papi/v0/groups')

	return (groups_result)

def getProperties(groupId, contractId):
	"""
	Get the properties for the associated group/contract combination
	"""
	print "Getting properties for group %s and contract %s" % (groupId, contractId)
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_result = httpCaller.getResult('/papi/v0/properties', property_parameters)
	
	if "properties" in property_result:
		property_items = property_result['properties']['items']
	else:
		property_items = []

	return (property_items)

def getPropertyInfo(propName, groupId, contractId):
	properties = getProperties(groupId, contractId)
	for property in properties:
		if property["propertyName"] == propName:
			return property

def getPropertyActivations(propertyId, groupId, contractId ):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_activations = httpCaller.getResult('/papi/v0/properties/%s/activations' % propertyId, 
								property_parameters)
	return (property_activations)



def getRealValue(version, property):
	if version == "STAGING":
		return property["stagingVersion"]
	if version == "PRODUCTION":
		return property["productionVersion"]
	if version == "LATEST":
		return property["latestVersion"]
	return version

def getPropertyVersion(property, version):
	result = {}
	property_parameters = { "contractId":property["contractId"],  "groupId":property["groupId"] }
	# We've got to get metadata, hostnames, and rules

	result_properties = httpCaller.getResult('/papi/v0/properties/%s/versions/%s'
								% (property["propertyId"], version),
								property_parameters)
	if "versions" not in result_properties:
		return
	result["meta"] = result_properties["versions"]["items"][0]

	hostname_results = httpCaller.getResult('/papi/v0/properties/%s/versions/%s/hostnames/'
								% (property["propertyId"], version),
								property_parameters)
	if "hostnames" in hostname_results and "items" in hostname_results["hostnames"] :
		if len(hostname_results["hostnames"]["items"])> 0:
			result["hostnames"] = hostname_results["hostnames"]["items"][0]

	rules_results = httpCaller.getResult('/papi/v0/properties/%s/versions/%s/rules/'
								% (property["propertyId"], version),
								property_parameters)
	if "rules" in rules_results:
		result["rules"]= rules_results["rules"]

	#print json.dumps(result, indent=2)
	return (result)	

if __name__ == "__main__":

	groupInfo = getGroup()
	first_account = groupInfo["accountId"]
	first_account_string = re.search('act_(.+?)$', first_account) 
	first_account = first_account_string.group(1)

	groups = groupInfo["groups"]["items"]

	for group in groups:
		groupId = group["groupId"]
		print "GroupId = %s:%s" % (group["groupId"], group["groupName"])
		if "contractIds" in group:
			for contractId in group["contractIds"]:
				properties = getProperties(groupId, contractId)
				for property in properties:
					if property["productionVersion"] != None or property["stagingVersion"] != None:
						property["activations"] = getPropertyActivations(property["propertyId"],
																		group["groupId"],
																		contractId)
					print json.dumps(property, indent=2)

					print "Latest Version is %s for %s" % (property["latestVersion"], property["propertyName"])
					for version in range(1, property["latestVersion"]+1):
						if property["propertyId"] == "prp_101920" and version < 40:
							continue
						property_version = getPropertyVersion(property, version)
						print "\n" + json.dumps(property_version, indent=2) + "\n"

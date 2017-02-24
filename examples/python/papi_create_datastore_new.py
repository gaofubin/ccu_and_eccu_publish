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
In order to create a datastore, you will need to have credentials
named 'papi' in the .edgerc file, and those credentials must have
read-only access to the property manager API.

Please send any comments, questions or ideas to open-developer@akamai.com

Thanks!
The Akamai Developer Relations Team

"""
import git
import requests, logging, json, random, sys, re, dateutil.parser, time
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
from http_calls import EdgeGridHttpCaller
import urllib
from subprocess import call, check_output
import os

g = git.Git()
session = requests.Session()
debug = False
verbose = False
section_name = "papi"

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

def getSingleProperty(propertyId, groupId, contractId ):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_result = httpCaller.getResult('/papi/v0/properties/%s/' % propertyId, 
								property_parameters)
	return (property_result)


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

	return (result)	


def createGitRepository():
	# Create the git repository, or change into it if it exists
	datastore = 'datastore'
	if not os.path.isdir(datastore): 
		os.makedirs(datastore) 
		git.Repo.init(datastore) 
	repo = git.Repo(datastore) 	
	os.chdir(datastore)
	return repo
	
def getExistingBranches():
	branches = g.branch()
	branches = branches.replace(" ","").replace("*","")
	branchlist = branches.split('\n')
	return branchlist

def getAccount(groupInfo):
	account = groupInfo["accountId"]
	account_string = re.search('act_(.+?)$', account)
	return account_string.group(1)

def gitCheckout(branch, existingProperties):
	if branch == "master":
		g.checkout('HEAD', "master")
		#repo.head.ref = repo.heads["master"]
	elif branch in existingProperties:
		g.checkout(branch)
		#repo.head.ref = repo.heads[branch]
		#repo.head.reset(index=True, working_tree=True)
		print "Returning 0"
		return 0
	else:
		repo.head.ref = repo.heads.master
		new_branch = repo.create_head(branch)
		repo.head.ref = repo.heads[branch]
		return 1

def additionalLabels(property, version):
	additionalLabels = []
	if version == property["latestVersion"]:
		additionalLabels.append(property["propertyName"] + "@" + "LATEST")
	if version == property["stagingVersion"]:
		additionalLabels.append(property["propertyName"] + "@" + "STAGING")
	if version == property["productionVersion"]:
		additionalLabels.append(property["propertyName"] + "@" + "PRODUCTION")
	print additionalLabels
	return additionalLabels

def createBranchFile(existingProperties, property, repo):
	new = gitCheckout(property["propertyName"], existingProperties)
	if os.path.exists("meta") and not new:
		with open('meta', 'r') as file:
			existing = json.load(file)
			file.close()
			return existing["propertyVersion"] + 1
	else:
		with open('branch', 'w+') as file:
			file.write(json.dumps(property, indent=2))
			file.close();
			repo.index.add(['branch'])

			repo.index.commit("Metadata for " + property["propertyName"])
			call(["git", "tag", property["propertyName"] + "_META"])
			return 1

if __name__ == "__main__":
	repo = createGitRepository()

	groupInfo = getGroup()
	existingProperties = getExistingBranches()

	# Create the account file
	account = getAccount(groupInfo)

	if not os.path.exists("account"):
		with open("account", "w+") as file:
			file.write(account)
			repo.index.add(["account"])
			repo.index.commit("Initial commit with account")
	 

	groups = groupInfo["groups"]["items"]

	for group in groups:
		if "contractIds" in group:	
			contractIds = group["contractIds"]
		else:
			continue
		print contractIds
		for contractId in contractIds:
			properties = getProperties(group["groupId"], contractId)
		
		for property in properties:
			if property == "master":
				continue
			print "Getting information for property %s" % property["propertyName"]
			numberToStart = createBranchFile(existingProperties, property, repo)
			print("Going from " + str(numberToStart) + " to " +  str(property["latestVersion"]))
			for version in range(numberToStart, property["latestVersion"]+1):
				print "   Getting version %s for %s" % (version, property["propertyName"])
				property_version = getPropertyVersion(property, version)
				if not property_version:
					continue
				with open('hostnames', 'w+') as file:
					if "hostnames" in property_version:
						file.write(json.dumps(property_version["hostnames"], indent=2))
				with open('meta', 'w+') as file:
					if "meta" in property_version:
						file.write(json.dumps(property_version["meta"], indent=2))
				with open('rules', 'w+') as file:
					if "rules" in property_version:
						file.write(json.dumps(property_version["rules"], indent=2))
				if version == 1:
					repo.index.add(["rules"])
					repo.index.add(["hostnames"])
					repo.index.add(["meta"])
				author = git.Actor(property_version["meta"]["updatedByUser"],  property_version["meta"]["updatedByUser"] + "@company.com")
				dt = dateutil.parser.parse(property_version["meta"]["updatedDate"])
				time = int(dt.strftime('%s'))
				os.environ["GIT_AUTHOR_DATE"] = "%s %s" % (time, "+0000")
				os.environ["GIT_COMMITTER_DATE"] = "%s %s" % (time, "+0000")
				repo.index.commit("Version " + property["propertyName"] + " : " + str(version), author=author, committer=author)
				tags = additionalLabels(property, version)
				tags.append(property["propertyName"] + "@" + str(version))
				for tag in tags:
					print "tagging: " + tag
					call(["git", "tag", tag])	

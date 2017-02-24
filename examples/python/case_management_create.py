#! /usr/bin/env python
# Case management script example.  This will create a test case, add a file, then
# request that it be closed.  

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
section_name = "casemanagement"

config = EdgeGridConfig({"verbose":debug},section_name)

if hasattr(config, "debug") and config.debug:
  debug = True

if hasattr(config, "verbose") and config.verbose:
  verbose = True

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token,
			max_body=131072
)

# Set the baseurl based on config.host
baseurl = '%s://%s/' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

if __name__ == "__main__":
	# This section demonstrates how to parse the output for categories
	# First, let's get a list of the categories available for case management
	categories_result = httpCaller.getResult("/case-management/v2/categories")
	# This will return several different categories_result
	for category in categories_result:
		if category["categoryType"] == "Technical":
			print "Information about the Technical category:"
			print json.dumps(category, indent=2)
	
	subcategories_result = httpCaller.getResult("/case-management/v2/categories/%s/sub-categories" % "Technical")
	# This is where you get the subCategoryType that you actually want to use for your calls
	mainType = subcategories_result["subCategory"]["subCategoryType"]
		
	subcats = subcategories_result["subCategory"]["subCategories"]
	for subcategory in subcats:
		displayName = subcategory["displayName"]
		subCategoryType = subcategory["subCategory"]["displayName"]
		# There is another level of nesting here, let's grab the right pieces
		for nestedcategory in subcategory["subCategory"]["subCategories"]:
			subCategoryValue = nestedcategory["subCategoryType"]
			sampleoutput = {
				"displayName" : displayName,
				"subCategoryType":mainType,
				"subCategoryValue":subCategoryValue
			}
			# This is how to structure the subcategory information you need to send to create a case
			print json.dumps(sampleoutput, indent=2)
			
	# For our case here, let's just pick the right category/sub-category
	# This is only a test ticket so we'll use that.  

	testCategory = "Technical"
	testSubCategories = [{
		"displayName": "Product",
		"subCategoryType":"product",
		"subCategoryValue":"Other"
	},
	{
		"displayName": "Problem",
		"subCategoryType":"problem",
		"subCategoryValue":"Duplicate/Test Ticket"
	}
	]

	# Now, to get the information about the case to be filed, you need to grab the case attributes.  You can pull
	# the information from this structure to get the pieces you need in order to create the case.

	attributes_params = {
		"product" : "Other",
		"problem":"Duplicate/Test Ticket"
	}
	attributes_result = httpCaller.getResult("/case-management/v2/categories/%s/case-attributes" % "Technical", attributes_params)
	print 
	print json.dumps(attributes_result,indent=2)

	newCase = {}

	# Set severity to the default value for the case
	newCase["severity"] = attributes_result["severity"]["value"]
	newCase["userDetail"] = {}
	for userField in ("userName", "userEmail","userPhone","userCompany"):
		newCase["userDetail"][userField] = attributes_result["userDetail"][userField]["value"]
	newCase["categoryType"] = testCategory
	newCase["subCategories"] = testSubCategories
	newCase["subject"] = "This is a test case from the Case Management API"

	print json.dumps(newCase, indent=2)
	
	case_create_result = httpCaller.postResult('/case-management/v2/cases', json.dumps(newCase))

	print json.dumps(case_create_result, indent=2)
	caseId = case_create_result["caseId"]

	files = {'file': open('case_management_create.py', 'rb')}
	case_upload_file_result = httpCaller.postFiles('/case-management/v2/cases/%s/files' % caseId, files)

	print json.dumps(case_upload_file_result)
	# List the active cases in the system 
	case_list_result = httpCaller.getResult('/case-management/v2/cases')
	print json.dumps(case_list_result, indent=2)

	closeComments = {"comment":"Closing API Generated case"}
	case_close_results = httpCaller.postResult('/case-management/v2/cases/%s/close-request' % caseId, closeComments)
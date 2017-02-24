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


Sample client for billing-center v2

NOTE: This code requires a single token configured with grants for the following:
* Billing Center API
* Contracts API

This client gets a list of your contracts and products and pulls information for
the first one of each, then retrieves billing usage for that combination.  It is
only designed to be an example of how to access the API, you'll need to use it
to guide your development.

The combination of calls should be sufficient to show
you how to do what you need with the billing-center API.

Contact open-developer@akamai.com with questions, ideas
or comments.

Thanks!
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
section_name = "billingcenter"

if sys.version_info[0] >= 3:
     # python3
     from urllib import parse
else:
     # python2.7
     import urlparse as parse


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

baseurl = '%s://%s/' % ('https', config.host)

httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

def getContractId():
	print
	print ("Requesting the first contract ID")

	contracts_result = httpCaller.getResult('/contract-api/v1/contracts/identifiers')
	return contracts_result[0]

def getProduct(contractId, productString):
	print
	print ("Requesting the %s product" % productString)
	productId = ""
	
	products_result = httpCaller.getResult('/contract-api/v1/contracts/%s/products/summaries' % contractId)

	for product in products_result['products']['marketing-products']:
		print ("Checking %s for %s" % (product['marketingProductName'], productString))
		if product['marketingProductName'] == productString:
			productId = product['marketingProductId']
			return productId

def getUsage(contractId, productId, parameters):
	print
	path = "/billing-center-api/v2/contracts/%s/products/%s/measures" % (contractId, productId)
	report_result = httpCaller.getResult(path, parameters)
	print (report_result)
	return report_result

if __name__ == "__main__":
	# getReportSources will return a list of reporting groups and/or contract ids
	# include the group or contract as contractId and the reportType as returned
	# by getReportSources
	# You could loop through them here, or just get one big kahuna report and chunk it up yourself
	contractId = getContractId()

	productId = getProduct(contractId, "HTTP Downloads")

	# Year and Month
	parameters = { 
		"year"   : 2016,
		"month"  : 8
	}

	# Grab the statistics
	usage = getUsage(contractId, productId, parameters)
	print (json.dumps(usage, indent=2))

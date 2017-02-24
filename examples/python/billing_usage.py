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


Sample client for billing-usage.

This client pulls the reportSources you have access to.
For the first result, it pulls all products.  Then it
creates monthly reports for the range you specify for
each product, and finally creates a CSV for the whole
range.  

The combination of calls should be sufficient to let
you do what you need with the billing-usage API.

Contact open-developer@akamai.com with questions, ideas
or comments.

Thanks!
"""

import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
if sys.version_info[0] >= 3:
     # python3
     from urllib import parse as encoder
     import urllib.parse as parse
else:
     # python2.7
     import urllib as encoder
     import urlparse as parse

session = requests.Session()
debug = False
verbose = False
section_name = "billingusage"

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

def getReportSources():
	print
	print ("Requesting the list of report sources")

	events_result = httpCaller.getResult('/billing-usage/v1/reseller/reportSources')
	print (events_result['contents'])
	return events_result['contents']

def getProducts(parameter_obj,startdate,enddate):
	print
	print ("Requesting a list of products for the given time period")
	headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json'}
	path = "/billing-usage/v1/products"

	parameters = {	"reportSources"	:parameter_obj,
			"startDate"	:startdate,
			"endDate"	:enddate
		}
  
	data_string = encoder.urlencode({p: json.dumps(parameters[p]) for p in parameters})
	products_result = session.post(parse.urljoin(baseurl,path),data=data_string, headers=headers)
	products_obj = json.loads(products_result.text)
	return products_obj['contents']

def getCsvReport(product_list, startdate, enddate, source_obj):
        print
        print ("Requesting a csv report for the given time period")
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        path = "/billing-usage/v1/contractUsageData/csv"

        parameters = {  "reportSources" :[source_obj],
			"products"	:product_list,
                        "startDate"     :startdate,
                        "endDate"       :enddate
                }
        print
        data_string = parse.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        products_result = session.post(parse.urljoin(baseurl,path),data=data_string, headers=headers)
        products_csv = products_result.text
        return products_csv

def getMeasures(product, startdate, enddate, source_obj):
	print
	print ("Requesting the list of measures valid for product %s" % product)
	parameters = {	'startMonth':startdate['month'],
			'endMonth':enddate['month'],
			'startYear':startdate['year'],
			'endYear':enddate['year'],
			'reportSourceId':source_obj['id'],
			'reportSourceType':source_obj['type'],
			'productId':product
			}
	path_string = '/'.join(['/billing-usage/v1/measures', product, source_obj['type'], source_obj['id'], startdate['month'], startdate['year'], enddate['month'], enddate['year']])
	measures_result = httpCaller.getResult(path_string)

def getStatisticTypes(product, startdate, enddate, source_obj):
	print
	print ("Requesting the list of statistic types valid for product %s" % product)
	parameters = {	'startMonth':startdate['month'],
			'endMonth':enddate['month'],
			'startYear':startdate['year'],
			'endYear':enddate['year'],
			'reportSourceId':source_obj['id'],
			'reportSourceType':source_obj['type'],
			'productId':product
			}
	path_string = '/'.join(['/billing-usage/v1/statisticTypes', product, source_obj['type'], source_obj['id'], startdate['month'], startdate['year'], enddate['month'], enddate['year']])
	statistics_result = httpCaller.getResult(path_string)
	return statistics_result['contents']

def getMonthlyReport(product, startdate, statistictype, source_obj):
	print
	path_string = '/'.join(['/billing-usage/v1/contractUsageData/monthly', product, source_obj['type'], source_obj['id'], statistictype, startdate['month'], startdate['year'],startdate['month'], startdate['year']])
	report_result = httpCaller.getResult(path_string)

if __name__ == "__main__":
	# getReportSources will return a list of reporting groups and/or contract ids
	# include the group or contract as contractId and the reportType as returned
	# by getReportSources
	# You could loop through them here, or just get one big kahuna report and chunk it up yourself
	reportSource = getReportSources()
	contractId = reportSource[0]['id']
	reportType = reportSource[0]['type']
	measures = {}
	statisticTypes = {}

	# Now, for a list of the products available for the reporting dates for these reporting sources

	source_obj = {
                "id" : contractId,
                "type" : reportType
        }

	startdate = {
		"month":"9", 
		"year":"2014"
	}
	
	enddate = {
		"month":"9",
		"year":"2014"
	}

	products = getProducts(source_obj, startdate, enddate)
	product_list = []
	for product in products:
		product_list.append({"id":product['id']})
		measures[product['id']] = getMeasures(product['id'], startdate, enddate, source_obj)
		statisticTypes = getStatisticTypes(product['id'], startdate, enddate, source_obj)
		for statisticType in statisticTypes:
			getMonthlyReport(product['id'],startdate,statisticType['statisticType'],source_obj)
		
	"""
	Get a CSV report for all products here, using the information we gathered above
	"""
	report = getCsvReport(product_list, startdate, enddate, source_obj)
	print (report)



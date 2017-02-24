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

Sample client for Media Analytics - Audience Analytics

This client pulls the report packs that are available, 
grabs the first data source for the first pack, and
then runs a request with all dimensions and metrics.

Put the credentials in ~/.edgerc using gen_edgerc.py
"""

import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
session = requests.Session()
debug = False
verbose = False
section_name = "media"

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

def getReportPacks():
	print
	report_packs_result = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs')
	return report_packs_result

def getReportPackInfo(reportpack):
	print
	report_pack_info = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s' % reportpack)
	return report_pack_info

def getDataStores(reportpack):
	print
	data_stores = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s/data-stores' % reportpack)
	return data_stores

def getData(reportpack,dimensionstring,metricstring):
	# Dimensions and metrics are retrieved with getReportPackInfo
	# Dimensions: Hourly viewers = 2002
	# Metrics: Service Provider = 942
	print
	parameters = {	'startDate': '09/01/2015:15:30',
			'endDate'  : '09/02/2016:15:30',
			'dimensions' : dimensionstring,
			'metrics'    : metricstring,
			'aggregation': 'day'
			}
	data_info = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s/data' % reportpack, parameters) 	
	
if __name__ == "__main__":
	reportpacks = getReportPacks()
	# To iterate over report packs, you can do a 
	reportpackinfo = getReportPackInfo(reportpacks[1]["id"])
	datastores = getDataStores(reportpacks[1]["id"])
	metrics = []
	dimensions = []
	datastore = datastores[17]
	for metric in datastore["metrics"]:
		if metric["id"] == 544:
			continue
		metrics.append(str(metric["id"]))
	for dimension in datastore["dimensions"]:
		if dimension["id"] == 845:
			continue
		dimensions.append(str(dimension["id"]))
	dimensionstring = ','.join(dimensions)
	metricstring = ','.join(metrics)

	print metricstring
	print dimensionstring

	getData(reportpacks[0]["id"],dimensionstring, metricstring)	


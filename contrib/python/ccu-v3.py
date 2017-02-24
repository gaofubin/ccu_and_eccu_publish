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


Sample client for CCU v3 API
Note that in order for this to work you need to provision credentials
specifically for CCU - you cannot extend existing credentials to add
CCU as it's managed under "CCU" in the API credential system.

Configure->Organization->Manage APIs
Select "CCU APIs"
Create client collections/clients
Add authorization

Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from http_calls import EdgeGridHttpCaller
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
import sys
session = requests.Session()
debug = False
verbose = False
section_name = "ccu"

logging.getLogger("requests").setLevel(logging.DEBUG) 

config = EdgeGridConfig({"verbose":False}, section_name, {"ccu_host":"store","ccu_paths":"store"})

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


def postPurgeRequest(host, paths):
	purge_obj = { "hostname": host,
                      "objects" : [ p for p in paths ]
		    }
	print "Invalidating  %s" % json.dumps(purge_obj)
	purge_post_result = httpCaller.postResult('/ccu/v3/invalidate/url', json.dumps(purge_obj))
	return purge_post_result

if __name__ == "__main__":
        if not config.ccu_host or not config.ccu_paths:
                print "The arguments --ccu_host and --ccu_paths must be specified"
                print "where "
                print "   --ccu_host is the hostname to invalidate and"
                print "   --ccu_path is the space separated list of paths to invalidate"
                print "For example:"
                print '   --ccu_host="example.com" --ccu_paths="/index.html /image.jpg"'
                exit(1)

        host = config.ccu_host
        paths = config.ccu_paths.split()
        print "invalidating paths %s on host %s"%(paths, host)
	purge_post_result = postPurgeRequest(host, paths)
        print "result:", purge_post_result

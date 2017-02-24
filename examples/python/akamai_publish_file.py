#! /usr/bin/env python
#ccu flush
import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib
import sys
session = requests.Session()
debug = False
verbose = False
section_name = "default"

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

if hasattr(config, 'headers'):
  session.headers.update(config.headers)

baseurl = '%s://%s' % ('https', config.host)
httpCaller = EdgeGridHttpCaller(session, debug,verbose, baseurl)

# ccu functions
def purge_by_urls(filename):
    data={
       "objects" : [
        	filename
       ]
    }
    print data
    result = httpCaller.postResult('/ccu/v3/delete/url/production', json.dumps(data, sort_keys=False, indent=4))
    print json.dumps(result, sort_keys=True, indent=4)
	
if __name__ == "__main__":
    if len(sys.argv) < 2:
      print "\033[;32m please input arguments \033[0m\n"
      exit()
    else:
      purge_by_urls(sys.argv[2])


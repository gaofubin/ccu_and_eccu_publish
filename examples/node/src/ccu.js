#! /usr/bin/env node

/**
Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at 

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

========================================================================

Example of using the Akamai OPEN CCU (Purge) API
https://developer.akamai.com/api/purge/ccu/overview.html

Helpful information:
- https://community.akamai.com/community/developer/blog/2015/08/19/getting-started-with-the-v2-open-ccu-api
*/

path = require('path'),
os = require('os'),
prettyJSON = require('prettyjson'),
logger = require('./logger'),
argv = require('minimist')(process.argv.slice(2));

// Akamai EdgeGrid signing library
var EdgeGrid = require('edgegrid');

// Optional command-line arguments
var debug = argv.debug ? true : false;
var verbose = argv.verbose ? true : false;
var headers = argv.headers ? argv.headers : {};

// The result data returned by the purge POST request
var purgePostResult;

// The path to the .edgerc file to use for authentication
var edgercPath = path.join(os.homedir(), "/.edgerc");

// The section of the .edgerc file to use for authentication
var sectionName = "ccu";

// Create a new instance of the EdgeGrid signing library
var eg = new EdgeGrid({
  path: edgercPath,
  section: sectionName,
  debug: debug
});

/**
 * Returns the current length of the default purge queue.
 */
function getPurgeQueueLength() {
  eg.auth({
    path: '/ccu/v2/queues/default',
    method: 'GET',
    headers: {},
    body: {}
  });

  eg.send(function(data, response) {
    data = JSON.parse(data);
    if (verbose) logger.logResponse(response);
    console.log("The queue currently has " + data.queueLength + " items in it.");
    addItemToQueue();
  });
}

/**
 * Add item to the default purge queue, and use the progressUri property of the 
 * response data to check the items purge status.
 */
function addItemToQueue() {

  var purgeObj = {
    action: "invalidate",
    objects: [
      "http://bc.akamaiapibootcamp.com/index.html"
    ]
  };

  eg.auth({
    path: "/ccu/v2/queues/default",
    method: "POST",
    body: purgeObj
  });

  console.log("Adding data to queue: " + JSON.stringify(purgeObj));

  eg.send(function(data, response) {
    data = JSON.parse(data);

    if (data.httpStatus == 201) {
      checkPurgeStatus(data.progressUri);
    } else {
      console.log("Request unsuccesful. Status " + data.httpStatus + " - " + data.detail);
    }
  });
}

/**
 * Call the progressUri received in the data returned from the POST request to
 * find out the current status of the Purge operation.
 *   
 * @param  {String} progressUri 
 */
function checkPurgeStatus(progressUri) {
  eg.auth({
    path: progressUri,
    method: "GET"
  });

  eg.send(function(data, response) {
    data = JSON.parse(data);
    if (verbose) logger.logResponse(response);
    console.log("You should wait " + data.pingAfterSeconds + " seconds before checking again.");
  });
}

getPurgeQueueLength();

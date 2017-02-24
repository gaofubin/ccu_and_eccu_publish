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
**/

/**
 * Example of using the Akamai OPEN diagnostic-tools API
 * https://developer.akamai.com/api/luna/diagnostic-tools/reference.html
 */

var path = require('path'),
  os = require('os'),
  prettyJSON = require('prettyjson'),
  argv = require('minimist')(process.argv.slice(2)),
  async = require('async'),
  logger = require('./logger'),
  EdgeGrid = require('edgegrid');

var debug = argv.debug ? true : false,
  verbose = argv.verbose ? true : false,
  sectionName = "default",
  edgercPath = path.join(os.homedir(), "/.edgerc"),
  headers = argv.headers ? argv.headers : {};

var eg = new EdgeGrid({
  path: edgercPath,
  section: sectionName,
  debug: debug
});

// Retrieve random location, then make a Dig request with it
async.waterfall([getLocations, makeDigRequest]);

/**
 * Retrieves a list of locations that can perform a dig request, then returns
 * a random location to be used in the Dig request.
 * 
 * @param  {Function} callback Callback that accepts location.
 */
function getLocations(callback) {
  eg.auth({
    path: '/diagnostic-tools/v1/locations',
    method: 'GET',
    headers: {},
    body: {}
  });

  eg.send(function(data, response) {
    console.log("Requesting locations that support the diagnostic-tools API...");

    // Pick random location
    data = JSON.parse(data);
    var locationCount = data.locations.length;
    var location = data.locations[Math.floor(Math.random() * locationCount)];

    if (verbose) logger.logResponse(response);
    console.log("\nThere are " + locationCount + " locations that can run dig in the Akamai Network,");
    console.log("We will make our call from " + location);

    // Return location to be used in Dig Request
    if (callback) return callback(null, location);
  });
}

function makeDigRequest(location, callback) {
  console.log("\nStarting dig request, this may take a moment...");

  // Perform dig request for developer.akamai.com using the Akamai server 
  // location specified and query type 'A' which performs a mapping to an IPv4
  // address
  var digParameters = {
    "hostname": "developer.akamai.com",
    "queryType": "A",
    "location": location
  };

  // Call auth, passing the query string parameters in via the 'qs' property
  eg.auth({
    path: '/diagnostic-tools/v1/dig',
    method: 'GET',
    headers: {},
    body: {},
    qs: digParameters
  });

  eg.send(function(data, response) {
    if (verbose) logger.logResponse(response);
    data = JSON.parse(data);
    console.log(data.dig.result);
  });
}

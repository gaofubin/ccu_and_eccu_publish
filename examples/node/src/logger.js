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

var prettyJSON = require('prettyjson');

function logResponse(response) {
  var body = response.body;
  var path = response.req.path;
  var status = response.statusCode;
  var method = response.request.method;
  var contentType = response.headers['content-type'];

  console.log(">>>\n" + prettyJSON.render(JSON.parse(body)) + "\n<<<\n");
  console.log("LOG: " + method + " " + path + " " + status + " " + contentType);
  logHTTPErrors(response, status, path);
}

function logHTTPErrors(response) {
  var path = response.req.path;
  var status = response.statusCode;
  var statusMsg = response.statusMessage;
  var errorMsg = "";

  if (status == 403) {
    errorMsg = "ERROR: Call to " + path + " failed with a 403 result.";
    errorMsg += "ERROR: This indicates a problem with authorization.";
    errorMsg += "ERROR: Please ensure that the credentials you created for this script.";
    errorMsg += "ERROR: have the necessary permissions in the Luna portal.";
    errorMsg += "ERROR: Problem details: " + statusMsg;
  }

  if (status == 400 || status == 401) {
    errorMsg = "ERROR: Call to " + path + " failed with a " + status + " result.";
    errorMsg += "ERROR: This indicates a problem with authentication or headers.";
    errorMsg += "ERROR: Please ensure that the .edgerc file is formatted correctly.";
    errorMsg += "ERROR: If you still have issues, please use gen_edgerc to re-generate the credentials.";
    errorMsg += "ERROR: Problem details: " + statusMsg;
  }

  if (status == 404) {
    errorMsg = "ERROR: Call to " + path + " failed with a " + status + " result.";
    errorMsg += "ERROR: This means that the page does not exist as requested.";
    errorMsg += "ERROR: Please ensure that the URL you're calling is correctly formatted.";
    errorMsg += "ERROR: or look at other examples to make sure yours matches.";
    errorMsg += "ERROR: Problem details: " + statusMsg;
  }

  if (errorMsg !== "") console.log(errorMsg);
}

module.exports = {
  logResponse: logResponse,
  loggHTTPErrors: logHTTPErrors
};

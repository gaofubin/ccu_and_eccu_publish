#!/usr/bin/env php
<?php
/**
 * Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 *
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * 
 * Very basic script demonstrating diagnostic tools functionality
 */
require_once __DIR__ . '/cli/init.php';

$client = Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile($configSection, $configFile);

# Request locations that support the diagnostic-tools
echo "Requesting locations that support the diagnostic-tools API.\n";

try {
    $response = $client->get('/diagnostic-tools/v1/locations');
    if ($response) {
        $result = json_decode($response->getBody());
    }

    $locations = sizeof($result->locations);
    
    printf("There are %s locations that can run dig in the Akamai Network\n", $locations);
    
    $location = $result->locations[rand(0, $locations - 1)];
    
    echo "We will make our call from " . $location . "\n";
    
    # Request the dig request the {OPEN} Developer Site IP informantion
    echo "Running dig from " . $location. "\n";
    
    $dig_parameters = [ "hostname" => "developer.akamai.com", "location" => $location, "queryType" => "A" ];
    $response = $client->get("/diagnostic-tools/v1/dig", ['query' => $dig_parameters]);
    if ($response) {
        $dig_result = json_decode($response->getBody());
    }
    
    # Display the results from dig
    echo $dig_result->dig->result;
} catch (GuzzleHttp\Exception\ClientException $e) {
    echo "An error occurred: " .$e->getMessage(). "\n";
    echo "Please try again with --debug or --verbose flags.\n";
}

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

$arguments = [
    'domain' => [
        'prefix' => 'D',
        'longPrefix' => 'domain',
        'description' => 'Site domain for Cloudlets policy',
        'required' => true
    ],
];

require_once __DIR__ . '/../cli/init.php';

$client = Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile($configSection, $configFile);

try {
    // Get Cloudlet
    echo "Fetching Cloudlet info: ";
    $url = '/cloudlets/api/v2/cloudlet-info';
    $response = $client->get($url);
    $cloudlets = json_decode($response->getBody());
    foreach ($cloudlets as $cloudlet) {
        if ($cloudlet->cloudletName == 'EDGEREDIRECTOR') {
            break;
        }
    }
    echo "done.\n";

    // Get Group
    echo "Fetching group info: ";
    $url = '/cloudlets/api/v2/group-info';
    $response = $client->get($url);
    $groups = json_decode($response->getBody());
    foreach ($groups as $group) {
        if (in_array($cli->arguments->get('domain'), $group->properties)) {
            break;
        }
    }
    echo "done\n";

    // Create cloudlet policy on group
    echo "Creating cloudlet policy: ";
    try {
        $url = '/cloudlets/api/v2/policies';
        $response = $client->post($url, [
            'body' => json_encode([
                'cloudletId' => $cloudlet->cloudletId,
                'groupId' => $group->groupId,
                'name' => 'example',
                'description' => 'Redirect to the example site'
            ]),
            'headers' => [
                'Content-Type' => 'application/json',
            ]
        ]);
        $policy = json_decode($response->getBody());
    } catch (\GuzzleHttp\Exception\ClientException $e) {
        if ($e->getResponse()->getStatusCode() !== 409) {
            throw $e;
        }
        $url = '/cloudlets/api/v2/policies';
        $response = $client->get($url);
        foreach (json_decode($response->getBody()) as $policy) {
            if ($policy->name === 'example') {
                break;
            }
        }
    }
    echo "done\n";

    // Get the current policy version
    echo "Fetching current policy version: ";
    $version = 1;
    foreach ($policy->activations as $network) {
        if ($network->network === 'prod') {
            $version = (int) $network->policyInfo->version + 1;
        }
    }
    echo "done.\n";

    // Redirect Rule
    $rule = [
        'description' => 'Match edge URL',
        'matchRuleFormat' => "1.0",
        'matchRules' => [
            [
                'name' => 'match-url',
                'type' => 'erMatchRule',
                'matchURL' => '/example',
                'statusCode' => 301,
                'redirectURL' => 'http://example.org/',
            ]
        ],
    ];

    // Add the rule
    echo "Adding redirect rule: ";
    $url = $policy->location . '/versions/' . $version;
    $response = $client->put($url, [
        'body' => json_encode($rule),
        'headers' => [
            'Content-Type' => 'application/json'
        ]
    ]);
    echo "done.\n";

    // Activate the policy
    echo "Activating policy: ";
    $policyVersion = json_decode($response->getBody());

    $url = $policyVersion->location . '/activations';
    $response = $client->post($url, [
        'body' => json_encode([
            "network" => "prod",
            "additionalPropertyNames"=> [ $cli->arguments->get('domain') ]
        ]),
        'headers' => [
            'Content-Type' => 'application/json'
        ]
    ]);
    echo "done.\n";

    echo "Rule activated!\n";
} catch (\GuzzleHttp\Exception\ClientException $e) {
    echo " failed.\n";
    exit;
}


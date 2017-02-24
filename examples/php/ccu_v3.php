#!/usr/bin/env php
<?php
/**
 * Copyright 2016 Akamai Technologies, Inc. All Rights Reserved.
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
 * Sample client for CCU
 * Note that in order for this to work you need to provision credentials
 *  specifically for CCU - you cannot extend existing credentials to add
 * CCU as it's managed under "CCU" in the API credential system.
 * 
 * Configure->Organization->Manage APIs
 * Select "CCU APIs"
 * Create client collections/clients
 * Add authorization
 *
 * Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
 */
namespace Akamai\Open\Example;

require_once __DIR__ . '/cli/init.php';

class CcuClient
{
	/**
	 * @var \Akamai\Open\EdgeGrid\Client
	 */
	protected $client;

	public function __construct()
	{
		$this->client = \Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile('ccu');
	}

	public function postPurgeRequest($hostname, $objects)
	{
		$purge_body = [
			'hostname' => $hostname,
			'objects' => $objects
		];

		$response = $this->client->post('/ccu/v3/invalidate/url', [
			'body' => json_encode($purge_body), 
			'headers' => ['Content-Type' => 'application/json']
		]);
		return $response;
	}
}

$ccu = new CcuClient();

try {
	$objects = [
		"/index.html",
		"/image.jpg"
	];

	$purge = $ccu->postPurgeRequest('akamaiapibootcamp.com', $objects);
	$response = json_decode($purge->getBody());
	echo 'Success (' .$purge->getStatusCode(). ')' . PHP_EOL;
	echo 'Estimated Purge Time: ' .$response->estimatedSeconds. 's' . PHP_EOL;
} catch (\GuzzleHttp\Exception\ClientException $e) {
	echo "An error occurred: " .$e->getMessage(). "\n";
	echo "Please try again with --debug or --verbose flags.\n";
}

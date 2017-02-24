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

	public function getQueue()
	{
		$response = $this->client->get('/ccu/v2/queues/default');
		printf("The queue currently has %s items in it\n", json_decode($response->getBody())->queueLength);
	}

	public function checkProgress($resource)
	{
		$response = $this->client->get($resource);
		return json_decode($response->getBody());
	}

	public function postPurgeRequest()
	{
		$purge_body = [
			"objects" => [
				"http://bc.akamaiapibootcamp.com/index.html"
			]
		];

		printf("Adding %s to queue\n", json_encode($purge_body, JSON_UNESCAPED_SLASHES));
		$response = $this->client->post('/ccu/v2/queues/default', [
			'body' => json_encode($purge_body), 
			'headers' => ['Content-Type' => 'application/json']
		]);
		return $response;
	}
}

$ccu = new CcuClient();

try {
	$ccu->getQueue();
	$purge = $ccu->postPurgeRequest();
	$progress = $ccu->checkProgress(json_decode($purge->getBody())->progressUri);

	$seconds_to_wait = $progress->pingAfterSeconds;
	printf("You should wait %s seconds before checking queue again...\n", $seconds_to_wait);
} catch (\GuzzleHttp\Exception\ClientException $e) {
	// Handle errors
	echo "An error occurred: " .$e->getMessage(). "\n";
	echo "Please try again with --debug or --verbose flags.\n";
}

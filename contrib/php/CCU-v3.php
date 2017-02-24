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
class Exception extends \Exception { }

class CCU
{
	/**
	 * Constant
	 */
	const BASE_URL = '/ccu/v3';
	const MAX_REQUEST_BODY = 50000; // bytes

	/**
	 * @var \Akamai\Open\EdgeGrid\Client
	 */
	protected $client;

	public function __construct($configSection=null, $configFile=null)
	{
		$this->client = \Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile($configSection,$configFile);
	}

	public function checkProgress($progressUri)
	{
		return $this->client->get($progressUri);
	}

	/**
	 * @action = invalidate, delete
	 * @type = url, cpcode
	 * @network = production, staging
	 * @objects = array of objects
	 */
	public function postRequest($action, $type, $network, $object)
	{
		if( count($object['objects']) < 1 )
			throw new Exception("Object is empty");

		$_body = json_encode($object);
		$_bodyLength = mb_strlen($_body);
		if( $_bodyLength >= self::MAX_REQUEST_BODY )
			throw new Exception("Body message is longer than maximum limit of ".self::MAX_REQUEST_BODY.": $_bodyLength");

		if( $action != 'invalidate' && $action != 'delete' )
			throw new Exception("Invalid action $action");

		if( $type != 'url' && $type != 'cpcode' )
			throw new Exception("Invalid type $type");

		if( $network != 'production' && $network != 'staging' )
			throw new Exception("Invalid network $network");

		$_URL = self::BASE_URL."/{$action}/{$type}/{$network}";
		$response = $this->client->post($_URL, [
			'body' => $_body,
			'headers' => ['Content-Type' => 'application/json']
		]);
		return $response;
	}

	/**
	 * Shorthand Methods
	 */
	public function invalidateCPCode($network, $object) { return $this->postRequest('invalidate','cpcode',$network,$object); }
	public function invalidateURL($network, $object) { return $this->postRequest('invalidate','url',$network,$object); }

	public function deleteCPCode($network, $object) { return $this->postRequest('delete','cpcode',$network,$object); }
	public function deleteURL($network, $object) { return $this->postRequest('delete','url',$network,$object); }
}

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

use Akamai\Open\Example\CCU as CCU;

require_once __DIR__ . '/cli/init.php';
require_once __DIR__ . '/CCU-v3.php';

$check_progress = false;
$debug = false;
$verbose = false;
$colors = array(
	'white'			=> "\033[0m",
	'red'			=> "\033[31;01m",
	'green'			=> "\033[32;01m",
	'yellow'		=> "\033[33;01m",
	'blue'			=> "\033[34;01m",
	'cyan'			=> "\033[36;01m",
	'white-bold'	=> "\033[37;01m",
);
define('SLEEP_RETRY', 5);	// seconds

define('HELP','HELP:
	-a, --action  : invalidate or delete
	-d, --debug   : Debug mode
	-f, --file    : Input file
	-n, --network : production or staging
	-p, --progress: check progress
	-t, --type    : url or cpcode
	-v, --verbose : Verbose mode

');

define('EXAMPLE',"EXAMPLE:
	{$argv[0]} -a invalidate -t url -n production -f url_file.txt
	or
	{$argv[0]} -a invalidate -t url -n production http://example.com/index.html http://example.com/logo.png

");

define('USAGE',"USAGE:
	{$argv[0]} -a[invalidate|delete] -t[url|cpcode] -n[production|staging] -[p] [[url|cpcode] ...]|-f[path_to_file]

");

// MANAGE ARGS
$parameters = array(
	'a:'	=> 'action:',
	'd'		=> 'debug',
	'f:'	=> 'file:',
	'n:'	=> 'network:',
	'p'		=> 'progress',
	't:'	=> 'type:',
	'v'		=> 'verbose',
);

function getObjectsFromFile($filename)
{
	$_content = trim(file_get_contents($filename));
	return preg_split("/[\s,]+/",$_content);
}

function url2obj($URLs)
{
	global $colors;
	$_obj = [
		'process'	=> [],
		'skip'	=> []
	];
	foreach( $URLs as $_url )
	{
		// Only accepts valid URL
		if( filter_var($_url, FILTER_VALIDATE_URL) !== false )
		{
			$_tmp = parse_url($_url);
			$_hostname = $_tmp['host'];
			$_path = $_tmp['path'];

			// Hostname is already in the list then append it
			if( array_key_exists($_hostname,$_obj['process']) )
				$_obj['process'][$_hostname]['objects'][] = $_path;
			
			// Create a new hostname list
			else $_obj['process'][$_hostname] = array (
					'hostname' => $_hostname,
					'objects' => [$_path]
				);
		}

		// Invalid URL
		else $_obj['skip'][] = $_url;
	}
	$_obj['process'] = array_values($_obj['process']);
	return $_obj;
}

function url2obj_new($URLs)
{
	global $colors;
	$_obj = [
		'process'	=> [],
		'skip'	=> []
	];
	foreach( $URLs as $_url )
	{
		// Only accepts valid URL
		if( filter_var($_url, FILTER_VALIDATE_URL) !== false ) $_obj['process']['objects'][] = $_url;

		// Invalid CP Code
		else $_obj['skip'][] = $_url;
	}
	return $_obj;
}

function cpcode2obj($CPCodes)
{
	global $colors;
	$_obj = [
		'process'	=> [],
		'skip'	=> []
	];
	foreach( $CPCodes as $_cpcode )
	{
		// Only accepts valid CP Code format
		if( is_numeric($_cpcode) ) $_obj['process'][0]['objects'][] = $_cpcode;

		// Invalid CP Code
		else $_obj['skip'][] = $_cpcode;
	}
	return $_obj;
}

function cpcode2obj_new($CPCodes)
{
	global $colors;
	$_obj = [
		'process'	=> [],
		'skip'	=> []
	];
	foreach( $CPCodes as $_cpcode )
	{
		// Only accepts valid CP Code format
		if( is_numeric($_cpcode) ) $_obj['process']['objects'][] = $_cpcode;

		// Invalid CP Code
		else $_obj['skip'][] = $_cpcode;
	}
	return $_obj;
}

function splitObjects($objects,$max_size)
{
	// TODO
	$_body = $objects['process']['objects'];
	$_json = json_encode($_body);
	$_length = mb_strlen($_json);
	$_split = ceil($_length/$max_size);
	echo "[$_length / $max_size = $_split]\n";
	print_r($_json);
	$_results = $_body;
	return $_results;
}

function batchRequests($action,$type,$network,&$objects)
{
	global $ccu,$colors,$verbose,$debug;

	for( $i=0; $i<count($objects); $i++ )
	{
		if( $type === 'url' )
		{
			echo ucfirst($action)." {$colors['green']}{$objects[$i]['hostname']}{$colors['white']}\n";
		}
		else
		{
			echo ucfirst($action)." {$colors['green']}".count($objects[$i])."{$colors['white']} CP Code(s)\n";
		}

		// VERBOSE: print request data
		if( isset($verbose) && $verbose )
		{
			echo "{$colors['cyan']}===> [VERBOSE] Request: \n";
			echo "{$colors['yellow']}".json_encode($objects[$i], JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT)."{$colors['white']}\n";
		}

		$objects[$i]['recheck'] = false;
		$_retry = true;
		while( $_retry )
		{
			try
			{
				$_response = json_decode((string) $ccu->postRequest($action,$type,$network,$objects[$i])->getBody());
				$_retry = false;
				$objects[$i]['success'] = true;
				$objects[$i]['response'] = $_response;

				if( isset($_response->pingAfterSeconds) && isset($_response->progressUri) ) $objects[$i]['recheck'] = true;

			}
			catch (\GuzzleHttp\Exception\ConnectException $e)
			{
				$_retry = true;
				$errorMessage = $e->getMessage();

				$objects[$i]['success'] = false;
				if( $e->hasResponse() )
					$objects[$i]['response'] = json_decode((string) $e->getResponse()->getBody());
			}
			catch (\GuzzleHttp\Exception\ServerException $e)
			{
				$_retry = true;
				$errorMessage = $e->getMessage();

				$objects[$i]['success'] = false;
				if( $e->hasResponse() )
					$objects[$i]['response'] = json_decode((string) $e->getResponse()->getBody());
			}
			catch (\GuzzleHttp\Exception\ClientException $e)
			{
				$_retry = false;
				$objects[$i]['success'] = false;
				if( $e->hasResponse() )
					$objects[$i]['response'] = json_decode((string) $e->getResponse()->getBody());
			}

			if( $_retry ) {
				echo "Unable to post request... {$colors['red']}retry in ".SLEEP_RETRY." seconds";
				echo "{$colors['white']}{$errorMessage}\n";
				sleep(SLEEP_RETRY);
			}
		}
	};
}

function checkProgress(&$objects)
{
	global $ccu,$colors,$verbose,$debug;

	$_maxCheck = 0;
	$_objCt = 0;
	for( $i=0; $i<count($objects); $i++ )
	{
		if( $objects[$i]['recheck'] )
		{
			if( $_maxCheck < $objects[$i]['response']->pingAfterSeconds ) $_maxCheck = $objects[$i]['response']->pingAfterSeconds;
			$_objCt++;
		}
	}

	if( $_objCt > 0 ) {
		echo "\nCheck Progress for $_objCt object(s) in $_maxCheck seconds...\n";
		sleep($_maxCheck);

		$_recheck = false;
		for( $i=0; $i<count($objects); $i++ )
		{
			if( $objects[$i]['recheck'] )
			{
				// TODO
				// try catch block
				$_response = json_decode((string) $ccu->checkProgress($objects[$i]['response']->progressUri)->getBody());
				$objects[$i]['response'] = $_response;
				if( isset($_response->pingAfterSeconds) && isset($_response->progressUri) ) {
					$objects[$i]['recheck'] = true;
					$_recheck = true;
				}
				else $objects[$i]['recheck'] = false;
			}
		}

		if( $_recheck ) checkProgress($objects);
	}
}

function reportResult($objects)
{
	global $colors,$verbose,$debug;

	echo "\n\033[1;4mSummary{$colors['white']}:\n";
	$skippedCt=count($objects['skip']);
	if( $skippedCt > 0 ) {
		echo "There are {$colors['red']}$skippedCt{$colors['white']} objects are {$colors['red']}skipped{$colors['white']}:\n";
		echo implode("\n",$objects['skip'])."\n";
	}

	foreach( $objects['process'] as $_object )
	{
		$_response = $_object['response'];
		$_color = $_object['success']?$colors['cyan']:$colors['red'];
		//print_r($_object);

		// URL
		if( isset($_object['hostname']) )
		{
			echo "{$_color}{$_response->httpStatus} {$colors['white']}{$_object['hostname']} ";

			if( $verbose )
				echo implode(",",$_object['objects'])."\n";
			else
				echo count($_object['objects'])." object(s)\n";
		}
		
		// CP Code
		else
		{
			echo "{$_color}{$_response->httpStatus} {$_response->title} {$colors['white']}";

			if( $verbose )
				echo implode(",",$_object['objects'])."\n";
			else
				echo count($_object['objects'])." object(s)\n";
		}
	}
}

// CHECK ARGS
if( $argc < 4 )
{ 
	echo USAGE.EXAMPLE;
	exit(1);
}

$opts = getopt(implode('',array_keys($parameters)), $parameters);

// Remove Params
$pruneargv = array();
foreach ($opts as $opt => $value)
{
	foreach ($argv as $key => $chunk)
	{
		$regex = '/^'. (isset($opt[1]) ? '--' : '-') . $opt . '/';
		if ($chunk == $value && $argv[$key-1][0] == '-' || preg_match($regex, $chunk))
		{
			array_push($pruneargv, $key);
		}
	}
}
while ($key = array_pop($pruneargv)) unset($argv[$key]);
unset($argv[0]);

foreach( array_keys($opts) as $opt ) switch( strtolower($opt) )
{
	// Action
	case 'a': case 'action':
		$action = strtolower($opts[$opt]);
		break;

	// Type
	case 't': case 'type':
		$type = strtolower($opts[$opt]);
		break;

	// Network
	case 'n': case 'network':
		$network = strtolower($opts[$opt]);
		break;

	// File
	case 'f': case 'file':
		$file = $opts[$opt];
		break;

	// Check Progress
	case 'p': case 'progress':
		$check_progress = true;
		break;

	// Verbose
	case 'v': case 'verbose':
		$verbose = true;
		break;

	// Debug
	case 'd': case 'debug':
		$debug = true;
		break;

	// Default/Help
	default:
		echo HELP.EXAMPLE.USAGE;
		break;
}

if( !isset($action) || !isset($type) || !isset($network) )
{ 
	echo "Invalid/missing arguments: ".implode(' ',$argv)."\n";
	echo HELP.EXAMPLE.USAGE;
	exit(1);
}

// Main function begins
$rawObjects = [];

// Get Objects from a file
if( isset($file) )
	$rawObjects = array_merge($rawObjects,getObjectsFromFile($file));

// Get Objects from arguments
if( count($argv) > 0 )
	$rawObjects = array_merge($rawObjects,array_values($argv));

// Convert to Object arrays
switch($type)
{
	case 'url':
		$objects = url2obj_new($rawObjects);
		break;

	case 'cpcode':
		$objects = cpcode2obj_new($rawObjects);
		break;

	default:
		$objects = [];
		break;
}

// Split object to be below CCU::MAX_REQUEST_BODY
//$objects = splitObjects($objects,CCU::MAX_REQUEST_BODY);
$objects = splitObjects($objects,100);

print_r($objects);

exit(0);

try
{
	$ccu = new CCU('default');
	batchRequests($action,$type,$network,$objects['process']);
	if( $check_progress ) checkProgress($objects['process']);
}
catch (Exception $e)
{
	// Handle errors
	echo get_class($e).": An error has occurred: {$colors['red']}" .$e->getMessage(). "{$colors['white']}\n";
	echo "Please try again with --debug or --verbose flags.\n";
	exit(1);
}
reportResult($objects);

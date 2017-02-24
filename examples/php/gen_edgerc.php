#!/usr/bin/env php
<?php
/**
 * Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 * 
 * Simple script to generate credentials file based on
 * Copy/paste of the "{OPEN} API Administration" output
 * Usage: php gen_edgerc.py <section_name>
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License. * 
 * You may obtain a copy of the License at * 
 * http://www.apache.org/licenses/LICENSE-2.0 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
require_once __DIR__ . '/cli/composer.php';

$cli = new League\CLImate\CLImate();
$cli->arguments->add(
	[
		'file' => [
			'prefix' => 'f',
			'longPrefix' => 'file',
			'description' => 'Path to credentials file to parse',
			'defaultValue' => null,
		],
		'help' => [
			'prefix' => 'h',
			'longPrefix' => 'help',
			'description' => 'Show this help',
			'defaultValue' => false,
			'noValue' => true
		],
		'section' => [
			'description' => '.edgerc section to create',
			'defaultValue' => 'default',
		],
	]
);

$cli->arguments->parse($_SERVER['argv']);

if ($cli->arguments->get('help')) {
	$cli->usage();
	exit;
}

define('HOME', $_SERVER['HOME']);
define('EDGERC', realpath(HOME . '/.edgerc') ?: realpath(HOME) . '/.edgerc' );
define('SECTION', $cli->arguments->get('section'));  

if ((file_exists(EDGERC) && !is_writable(EDGERC)) || !is_writable(HOME)) {
	$cli->to('error')->error("Unable to write to file " . EDGERC);
	exit(-1);
}

echo "After authorizing your client in the {OPEN} API Administration tool,\n";
echo "export the credentials and paste the contents of the export file below,\n"; 
echo "followed by control-D. (You may need to enter is twice)\n";
echo ">>> ";

$inputStream = fopen('php://stdin', 'r+');
if (!$file = $cli->arguments->get('file')) {
	$input = stream_get_contents($inputStream);
} elseif (file_exists($file) && is_readable($file)) {
	$input = file_get_contents($file); 
}

$cli = new League\CLImate\CLImate();
$cli->out("");
if (file_exists(EDGERC)) {
	$cli->bold()->info("Updating Existing .edgerc File");
	$file = parse_ini_file(EDGERC, true, INI_SCANNER_RAW);
	if (isset($file[SECTION])) {
		$response = $cli->bold()->cyan()
			->input("Update existing section? (" .SECTION. ") [Y/n]")
			->prompt();
		if (strtolower($response) != 'y' && !empty($response)) {
			$cli->error("This script will now exit.");
			exit(-1);
		}
	} else {
		$cli->lightBlue("Adding new section: " .SECTION);
	}
} else {
	$cli->info("Creating new .edgerc file");
	$cli->lightBlue("Adding new section: " . SECTION);
}

foreach (parse($input) as $key => $value) {
	$file[SECTION][$key] = $value;
}

$out = '';
foreach ($file as $section => $config) {
	$out .= "[$section]\n";
	foreach ($config as $key => $value) {
		$out .= "$key = $value\n";
	}
	$out .= "\n";
}

if (!file_put_contents(EDGERC, $out)) {
	$cli->error("Something went wrong trying to write the file! (" .EDGERC. ")");
	exit(-1);
}

$cli->info("Success!");
exit;

function parse($file) {
	$map = [
		'secret' => 'client_secret',
		'base url' => 'host',
		'access tokens' => 'access_token',
		'client token' => 'client_token',
	];
	$file = preg_replace(["/\n+/", "/\t+/", "/ +/"], ["\n", "\t", " "], $file);
	$tokens = [];
	preg_match_all('/
		(?:Client\sCredentials:\s+)? 	# If it starts with Client Credentials: ignore it
		(?:\s*)(?<name>.+?) 			# Match the field name
		:\s+ 							# Match the : and space after field name
		(?:https:\/\/)? 				# If there is a url scheme ignore it
		(?<value>[^\s]+)				# Match the value
		/x', $file, $tokens, PREG_SET_ORDER);

	foreach ($tokens as $token) {
		$token['name'] = strtolower($token['name']);
		if (!isset($map[$token['name']])) {
			continue;
		}
		yield $map[$token['name']] => $token['value'];
	}

	yield "max-body" => "131072";
}
?>

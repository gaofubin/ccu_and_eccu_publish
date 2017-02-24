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
 *
 * Sample client for billing-usage.
 *
 * This client pulls the reportSources you have access to.
 * For the first result, it pulls all products.  Then it
 * creates monthly reports for the range you specify for
 * each product, and finally creates a CSV for the whole
 * range.
 *
 * The combination of calls should be sufficient to let
 * you do what you need with the billing-usage API.
 *
 * Contact open-developer@akamai.com with questions, ideas
 * or comments.
 *
 * Thanks!
 */
namespace Akamai\Open\Example;

require_once __DIR__ . '/cli/init.php';

class BillingUsageClient
{
	/**
	 * @var \Akamai\Open\EdgeGrid\Client
	 */
	protected $client;

	public function __construct()
	{
		$this->client = \Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile('billingusage');
	}

	public function  getReportSources()
	{
		echo "\nRequesting the list of report sources\n";
	
		$response = $this->client->get('/billing-usage/v1/reseller/reportSources', ['Accept' => 'application/json']);
		$sources = json_decode($response->getBody());
		
		return $sources->contents;
	}

	public function  getProducts($reportSources, $startDate, $endDate)
	{
		echo "\nRequesting a list of products for the given time period\n";
		$headers = ['Content-Type' => 'application/x-www-form-urlencoded; charset=UTF-8','Accept' => 'application/json'];
		$path = "/billing-usage/v1/products";
	
		$parameters = [
			"reportSources" => $reportSources,
			"startDate" => $startDate,
			"endDate" => $endDate
		];
		
		$parameters = array_map('json_encode', $parameters);
		
		$response = $this->client->post($path, ['form_params' => $parameters, 'headers' => $headers]);
		$products = json_decode($response->getBody());
		return $products->contents;
	}

	public function  getCsvReport($productList, $startDate, $endDate, $source)
	{
			echo "\nRequesting a csv report for the given time period\n";
			$headers = ['Content-Type' => 'application/x-www-form-urlencoded; charset=UTF-8','Accept' => '*/*'];
			$path = "/billing-usage/v1/contractUsageData/csv";
	
			$parameters = [
				"reportSources" => [$source],
				"products" => $productList,
				"startDate" => $startDate,
				"endDate" => $endDate
			];
		
			$parameters = array_map('json_encode', $parameters);
				
			$response = $this->client->post($path, ['form_params' => $parameters, 'headers' => $headers]);
			$products = (string) $response->getBody();
			return $products;
	}

	public function  getMeasures($product, $startDate, $endDate, $source)
	{
		printf("\nRequesting the list of measures valid for product %s\n", $product);
		
		$path = implode('/', ['/billing-usage/v1/measures', $product, $source['type'], $source['id'], $startDate['month'], $startDate['year'], $endDate['month'], $endDate['year']]);
		$response = $this->client->get($path);
		return (string) $response->getBody();
	}
	
	public function  getStatisticTypes($product, $startDate, $endDate, $source)
	{
		printf("\nRequesting the list of statistic types valid for product %s\n", $product);

		$path = implode('/', ['/billing-usage/v1/statisticTypes', $product, $source['type'], $source['id'], $startDate['month'], $startDate['year'], $endDate['month'], $endDate['year']]);
		$response = $this->client->get($path);
		return json_decode($response->getBody())->contents;
	}
	
	public function  getMonthlyReport($product, $startDate, $statisticType, $source)
	{
		$path = implode('/', ['/billing-usage/v1/contractUsageData/monthly', $product, $source['type'], $source['id'], $statisticType, $startDate['month'], $startDate['year'], $startDate['month'], $startDate['year']]);
		$report = $this->client->get($path);
		return (string) $report->getBody();
	}
}

/*
 * getReportSources will return a list of reporting groups and/or contract ids
 * include the group or contract as contractId and the reportType as returned
 * by getReportSources
 * You could loop through them here, or just get one big kahuna report and chunk it up yourself
 */
$client = new BillingUsageClient();

try {
	$reportSource = $client->getReportSources();
	$contractId = $reportSource[0]->id;
	$reportType = $reportSource[0]->type;
	$measures = [];
	$statisticTypes = [];

	# Now, for a list of the products available for the reporting dates for these reporting sources

	$source = [
		"id" => $contractId,
		"type" => $reportType
	];

	$startDate = [
		"month" => "9",
		"year" => "2014"
	];

	$endDate = [
		"month" => "9",
		"year" => "2014"
	];

	$products = $client->getProducts($source, $startDate, $endDate);
	$productList = [];
	foreach ($products as $product) {
		$productList[] = ["id" => $product->id];
		$measures[$product->id] = $client->getMeasures($product->id, $startDate, $endDate, $source);
		$statisticTypes = $client->getStatisticTypes($product->id, $startDate, $endDate, $source);
		foreach ($statisticTypes as $statisticType) {
			echo $client->getMonthlyReport($product->id, $startDate, $statisticType->statisticType, $source) . "\n";
		}
	}


	/*
	 * Get a CSV report for all products here, using the information we gathered above
	 */
	$report = $client->getCsvReport($productList, $startDate, $endDate, $source);
	echo $report . "\n";
} catch (\GuzzleHttp\Exception\ClientException $e) {
	// handle errors
	echo "An error occurred: " .$e->getMessage(). "\n";
	echo "Please try again with --debug or --verbose flags.\n";
}



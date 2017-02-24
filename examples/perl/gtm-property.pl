#! /usr/bin/env perl
# Very basic script demonstrating diagnostic tools functionality
#
# Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at 
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

use Akamai::Edgegrid;
use Config::IniFiles;
use JSON;
use strict;
use warnings;
use URI; 
use Getopt::Long;

my %args;

my $debug = 0;
my $verbose = 0;

GetOptions ("debug" => \$debug, 
            "verbose"  => \$verbose)
  or die("Error in command line arguments\n");

my $config_file = "$ENV{HOME}/.edgerc";
my $section = "gtm";

my $agent = new Akamai::Edgegrid( 
			config_file => $config_file, 
			section   => $section,
			debug     => $debug );
my $baseurl = "https://" . $agent->{host};
my $json = JSON->new->utf8->pretty(1);

#######################
# MAIN                #
#######################

my $domainname = "akamaiapibootcamp.com.akadns.net";
my $propertyname = "origin";

my $endpoint = "$baseurl/config-gtm/v1/domains/$domainname/properties/$propertyname";
# First, get the existing property
my $response = $agent->get( $endpoint);
my $property_object = decode_json($response->content);
if ($verbose == 1) {print encode_json($property_object); }

my $req = HTTP::Request->new(
	PUT => "$endpoint");
$req->content_type('application/json');

$$property_object{"trafficTargets"}[0]{"weight"} = 1;
$$property_object{"trafficTargets"}[1]{"weight"} = 1;

my $content = encode_json($property_object);
$req->content($content);

$response = $agent->request( $req );
my $response_object = decode_json($response->content);
if ($verbose == 1) {print $json->encode($response_object); }


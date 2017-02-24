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
my $section = "default";

my $agent = new Akamai::Edgegrid( 
			config_file => $config_file, 
			section   => $section,
			debug     => $debug );
my $baseurl = "https://" . $agent->{host};
my $json = JSON->new->utf8->pretty(1);

sub getLocations {
	# Grab the locations from the system
	my $response = $agent->get( "$baseurl/diagnostic-tools/v1/locations");
	my $location_object = decode_json($response->content);
	if ($verbose == 1) {print $json->encode($location_object); }
	return $location_object;
}

sub runDig {
	my ($target, $location) = @_;
	# Set the parameters for the call, and append them to the URL
	my %parameters = (
                       	location => $location,
			hostname => $target,
			queryType => 'A' 
        );
	my $url = URI->new("$baseurl/diagnostic-tools/v1/dig");
	$url->query_form(%parameters);
        my $response = $agent->get( $url );
	my $dig_object = decode_json($response->content);
	if ($verbose == 1) {print $json->encode($dig_object); }
        return $dig_object ;
}

#######################
# MAIN                #
#######################
# Grab the locations  #
#######################
print "Getting the locations to run 'dig' from\n";
my @locations = @{ getLocations()->{locations}};

print "There are " . scalar(@locations) . " locations available.\n";

#######################
# Select a random loc #
#######################

my $random_index = int(rand($#locations));
my $location = $locations[$random_index];

print "We will run the dig from $location.\n";

#######################
# Run dig             #
#######################

my $dig_hash = runDig("developer.akamai.com",$location);

print $$dig_hash{"dig"}{"result"};


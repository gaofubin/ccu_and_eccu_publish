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
my $section = "ccu";

my $agent = new Akamai::Edgegrid( 
			config_file => $config_file, 
			section   => $section,
			debug     => $debug );
my $baseurl = "https://" . $agent->{host};
my $json = JSON->new->utf8->pretty(1);

#######################
# MAIN                #
#######################

########################
# Post a purge request #
########################

my $req = HTTP::Request->new(
	POST => "$baseurl/ccu/v3/invalidate/url");
$req->content_type('application/json');

my $content = '{ "hostname":"bc.akamaiapibootcamp.com", "objects" : [ "/index.html" ] }';
print $content;
$req->content($content);

my $response = $agent->request( $req );
my $purge_object = decode_json($response->content);
if ($verbose == 1) {print $json->encode($purge_object); }



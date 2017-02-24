#!/usr/bin/perl
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
my $section = "networklists";

my $agent = new Akamai::Edgegrid( 
			config_file => $config_file, 
			section   => $section,
			debug     => $debug );
my $baseurl = "https://" . $agent->{host};
my $json = JSON->new->utf8->pretty(1);

#######################
# MAIN                #
#######################

print "Printing the list of network lists";

if ( $verbose == 1 ) {
    my $endpoint = "$baseurl/network-list/v1/network_lists";
    # First, get the existing network list
    my $response = $agent->get( $endpoint );
    my $network_list_object = $json->decode( $response->content );
    print $json->encode( $network_list_object );
}

# POST to create a new list (commented out by default)

my $req = HTTP::Request->new(
	POST => "$endpoint");
$req->content_type('application/json');

my %new_list_object = ( "list" => [ "8.8.8.8" ],
                        "name" => "test",
                        "type" => "IP" );

my $content = encode_json(\%new_list_object);
$req->content($content);

# Uncomment here to actually create the list
# $response = $agent->request( $req );
# my $response_json = $response->content;
# if ($verbose == 1) {print $response_json; }
# print $response->status_line . "\n";

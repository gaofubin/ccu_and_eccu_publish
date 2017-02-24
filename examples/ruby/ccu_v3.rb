#!/usr/bin/env ruby

=begin
Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.


Sample client for CCU
Note that in order for this to work you need to provision credentials
specifically for CCU - you cannot extend existing credentials to add
CCU as it's managed under "CCU" in the API credential system.

Configure->Organization->Manage APIs
Select "CCU APIs"
Create client collections/clients
Add authorization

Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
=end

require 'akamai/edgegrid'
require 'net/http'
require 'uri'
require 'json'
require 'optparse'

address = get_host("~/.edgerc","ccu")

      http = Akamai::Edgegrid::HTTP.new(
        address = address,
        port = 443,
      )


options = {}

OptionParser.new do |opts|
	opts.banner = "Usage: diagnostic-tools.rb [opts]"

	opts.on("-v", "--verbose", "Run verbosely") do |v|
    	options[:verbose] = v
  	end
  	opts.on("-d", "--debug", "Run with debug") do |v|
    	http.set_debug_output $stderr
  	end
end.parse!

baseuri = URI('https://' + http.host)

http.setup_from_edgerc(:section => "ccu")

def postPurgeRequest(baseuri, http, options, action="invalidate")
	post_request = Net::HTTP::Post.new(
    	URI.join(baseuri.to_s, "/ccu/v3/invalidate/url").to_s,
    	initheader = { 'Content-Type' => 'application/json' }
	)

	post_request.body = {
    	:hostname => "bc.akamaiapibootcamp.com",
    	:objects => [
				"/index.html"
			]
	}.to_json

	post_response = http.request(post_request)
	if options[:verbose]
		puts JSON.pretty_generate(JSON.parse(post_response.body))
	end

	return JSON.parse(post_response.body)

end


# Here's the main execution area for the program
# Add a purge request

puts "Adding to queue"
postresult = postPurgeRequest(baseuri,http,options)
puts postresult["detail"]




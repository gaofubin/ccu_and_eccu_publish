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

def getQueue(baseuri,http,options)
	puts "Getting request"
	request = Net::HTTP::Get.new URI.join(baseuri.to_s, '/ccu/v2/queues/default').to_s
	response = http.request(request)
	puts "Got request"
	if options[:verbose]
		puts JSON.pretty_generate(JSON.parse(response.body))
	end

	length = JSON.parse(response.body)["queueLength"] # Grab the locations array from the result
	return "There are currently #{length} items in the queue"
end

def postPurgeRequest(baseuri, http, options, action="invalidate")
	post_request = Net::HTTP::Post.new(
    	URI.join(baseuri.to_s, "/ccu/v2/queues/default").to_s,
    	initheader = { 'Content-Type' => 'application/json' }
	)

	post_request.body = {
    	:action => action,
    	:objects => [
				"http://bc.akamaiapibootcamp.com/index.html"
			]
	}.to_json

	post_response = http.request(post_request)
	if options[:verbose]
		puts JSON.pretty_generate(JSON.parse(post_response.body))
	end

	return JSON.parse(post_response.body)

end

def checkProgress(resource, baseuri, http, options)
	request = Net::HTTP::Get.new URI.join(baseuri.to_s, resource).to_s
	response = http.request(request) 
	if options[:verbose]
		puts JSON.pretty_generate(JSON.parse(response.body))
	end

	return JSON.parse(response.body)["purgeStatus"]
end


# Here's the main execution area for the program
# Get the Queue
# Add a purge request
# Get the Queue
# Check the purge request
puts "Checking queue"
puts getQueue(baseuri,http,options)

puts "Adding to queue"
postresult = postPurgeRequest(baseuri,http,options)
puts postresult["detail"]

puts "Checking queue again"
puts getQueue(baseuri,http,options)

puts "Checking status for post request"
puts checkProgress(postresult["progressUri"],baseuri,http,options)



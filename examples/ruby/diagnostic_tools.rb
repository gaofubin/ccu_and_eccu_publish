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

=end

require 'akamai/edgegrid'
require 'net/http'
require 'uri'
require 'json'
require 'optparse'
address = get_host()

      http = Akamai::Edgegrid::HTTP.new(
	address=address,
        port=443
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

http.setup_from_edgerc({})

request = Net::HTTP::Get.new URI.join(baseuri.to_s, 'diagnostic-tools/v1/locations').to_s
response = http.request(request)
if options[:verbose]
	puts JSON.pretty_generate(JSON.parse(response.body))
end
locations = JSON.parse(response.body)["locations"] # Grab the locations array from the result

puts "There are #{locations.length} locations to run dig from, selecting one at random."

location_index = 1+rand(locations.length)

puts "Using the location #{locations[location_index]}"

# To use parameters, we need to go through another step
uri = URI.join(baseuri.to_s, 'diagnostic-tools/v1/dig')
uri.query = URI.encode_www_form({:location => locations[location_index], :queryType => "A", :hostname => "developer.akamai.com"})
request = Net::HTTP::Get.new uri.to_s

response = http.request(request)
if options[:verbose]
	puts JSON.pretty_generate(JSON.parse(response.body))
end

puts JSON.parse(response.body)["dig"]["result"]



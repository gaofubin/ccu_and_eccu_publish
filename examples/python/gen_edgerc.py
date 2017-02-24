#! /usr/bin/env python

# This script will generate a ~/.edgerc credentials file based on
# the output of the "{OPEN} API Administration" tool in Luna Control Center.
#
# Usage: python gen_edgerc.py -s <section_name> -f <export_file>

""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at 
    http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys, os
import re
import argparse

if sys.version_info[0] >= 3:
     # python3
     import configparser as ConfigParser
else:
     # python2.7
     import ConfigParser


from os.path import expanduser

# This script will create a configuration section with the name of the client in your 
# ~/.edgerc credential store. Many of the sample applications use the a section 
# named 'default' for ease when running them during API Bootcamps.  

parser = argparse.ArgumentParser(description='After authorizing your client \
	in the {OPEN} API Administration tool, export the credentials and process \
	them with this script.')
parser.add_argument('--config_section', '-s', action='store', 
	help='create new config section with this section name.')
parser.add_argument('--cred_file', '-f', action='store', 
	help='use the exported file from the OPEN API Administration tool.')
args= parser.parse_args()

# Determine the section name giving precedence to -s value
if args.config_section:
	section_name = args.config_section
	section_name_pretty = args.config_section
if not args.config_section or args.config_section.lower() == "default":
	section_name = "----DEFAULT----"
	section_name_pretty = "default"

print ("Akamai OPEN API EdgeGrid Credentials")
print
print ("This script will create a '%s' section in the local ~/.edgerc credential file." % section_name_pretty)
print

if args.cred_file:
	print ("+++ Reading from EdgeGrid credentials file:", args.cred_file)
	with open (os.path.expanduser(args.cred_file), "r") as credFile:
			text = credFile.read()
			credFile.close()
else:
	print ("After authorizing your client in the {OPEN} API Administration tool,")
	print ("export the credentials and paste the contents of the export file below," )
	print ("followed by control-D.")
	print
	sys.stdout.write('>>>\n')
	text = sys.stdin.read()

home = expanduser("~")
index = 0
fields = {}


# Process the original .edgerc file
origConfig = ConfigParser.ConfigParser()
filename = "%s/.edgerc" % home

# If this is a new file, create it
if not os.path.isfile(filename):
	print ("+++ Creating new credentials file: %s" % filename)
	open(filename, 'a+').close()
else:
	print ("+++ Found credentials file: %s" % filename)
	
origConfig.read(filename)

if section_name_pretty in origConfig.sections():
	print (">>> Replacing section: %s" % section_name_pretty)
	sys.stdout.write ("*** OK TO REPLACE section %s? *** [Y|n]:" % section_name_pretty)
	choice = raw_input().lower()
	if choice == "n":
		print "Not replacing section."
		exit(0)

	replace_section = True
else:
	print ("+++ Creating section: %s" % section_name_pretty)
	replace_section = False

# We need a line for the output to look nice
print 

# If we have a 'default' section hide it from ConfigParser
with open (filename, "r+") as myfile:
	data=myfile.read().replace('default','----DEFAULT----')
	myfile.close()
with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

# Open the ~/.edgerc file for writing
Config = ConfigParser.ConfigParser()
Config.read(filename)
configfile = open(filename,'w')

# Add the new section
if not Config.has_section(section_name):
	Config.add_section(section_name)

# load the cred data

if "Secret:" in text:
	fieldlist = text.split()
	# Parse the cred data
	while index < len(fieldlist):
		if (re.search(r':$', fieldlist[index])):
			fields[fieldlist[index]] = fieldlist[index + 1]
		index += 1
	Config.set(section_name,'client_secret',fields['Secret:'])
	Config.set(section_name,'host',fields['URL:'].replace('https://',''))
	Config.set(section_name,'access_token',fields['Tokens:'])
	Config.set(section_name,'client_token',fields['token:'])

else:
	lines = text.split('\n')
	for line in range(len(lines)-1):
		if not lines[line].strip():
			continue
		(field, value) = lines[line].split(' = ')
		Config.set(section_name,field,value)
Config.write(configfile)

configfile.close()

# Undo the ConfigParser work around
with open (filename, "r") as myfile:
	data=myfile.read().replace('----DEFAULT----','default')
	myfile.close()

with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

print ("\nDone. Please verify your credentials with the verify_creds.py script using verify_creds.py -s %s." % section_name_pretty)
print	

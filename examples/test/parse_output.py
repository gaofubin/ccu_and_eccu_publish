# This command generates a valid xml file for junit parsing in Jenkins
# It is designed to create the minimum valid xml file for the purpose, as demonstrated here:
#<testsuite tests="3">
#    <testcase classname="foo1" name="ASuccessfulTest"/>
#    <testcase classname="foo2" name="AnotherSuccessfulTest"/>
#    <testcase classname="foo3" name="AFailingTest">
#        <failure type="NotEnoughFoo"> details about failure </failure>
#    </testcase>
#</testsuite>
#
#
# To run, call parse_output.py <scriptname> <dig>
#
# % generate_junit.py diagnostic_tools dig

import sys, glob, re, string
import time
from datetime import datetime
from tzlocal import get_localzone
import pytz

local_tz = get_localzone() 
ts = time.time()
utc_now, now = datetime.utcfromtimestamp(ts), datetime.fromtimestamp(ts)
local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_tz)
assert local_now.replace(tzinfo=None) == now


if len(sys.argv) < 3:
	exit('Usage: %s <scriptname_base> <classname>' % sys.argv[0])

scriptname = sys.argv[1]
name = sys.argv[2]
now = local_now.isoformat()
now = now[:-13] + now[-6:]

error_results = {}
output_results = {}

for file in glob.glob("%s.*.*" % scriptname):
	if "error" in file:
		with open (file, 'r') as error_file:
			error_results[file] = error_file.read()	

	if "output" in file:
		with open (file, 'r') as output_file:
			output_content = string.split(output_file.read(),'\n')
			base_filename = file[:-7]
			output_string = ""
			method = ""
			endpoint = ""
			status = ""
			for line in output_content:
				if ".py" in base_filename: 
					if "LOG: " in line:
						output_string = "%s %s %s" % (line[5:],base_filename,now)
						print output_string
				elif ".php" in base_filename:
					if "> GET" in line or "> POST" in line:
						items = string.split(line,' ')
						method = items[1]
						endpoint = string.split(items[2],'?')[0]
					if "< HTTP/1.1" in line:
						status = line[11:14]
					if "< Content-Type:" in line:
						content_type = line[16:-1]
						output_string = "%s %s %s %s %s %s" % (method, endpoint, status, content_type,base_filename,now)
						print output_string
			output_results[file] = output_file.read()

with open ('test.xml', 'w') as xml_file:
	# One test per script
	xml_file.write('<testsuite tests="%d">\n' % len(output_results))
	for key in output_results:
		xml_file.write('    <testcase classname="%s" name="%s"' % (key, name))
		if key in error_results:
			xml_file.write('>\n')	
			xml_file.write('       <failure type="fail">%s\n       </failure>\n' % error_content[key])
			xml_file.write('    </testcase>\n')
		else:
			xml_file.write('/>\n')
	xml_file.write('</testsuite>\n')
	xml_file.close()

# Node.js Example Code

This will guide you through the steps necessary to set up credentials and start playing with the sample code. These instructions expect that you are in the examples/node subdirectory of the github repository.

> __Note:__ Once you've set up credentials for one language, you don't need to re-create them for another language. So, if you've already set up the credentials for python, or php, you do not need to recreate them again here.

# Authentication and Provisioning
The easiest way to walk through the provisioning and authentication required to get your credentials is by following the instructions on [Authorizing Your Client](https://developer.akamai.com/introduction/Prov_Creds.html) from the Getting Started Guide on [developer.akamai.com](https://developer.akamai.com). Once you have done this, you'll be able to run the 'diagnostic tools' example script described below.

## Credential File Creation
You can get your credentials set up for use by the sample code by using the gen_edgerc command in the examples/node directory. A full set of instructions on using this script is available at [https://www.npmjs.com/package/akamai-gen-edgerc](https://www.npmjs.com/package/akamai-gen-edgerc), but the most basic example simply requires running the `gen_edgerc` command and pasting the contents of your client authorization file as follows:

```bash
$ gen_edgerc 
This script will create a section named 'default' in the local file /Users/ktyacke/.edgerc.

After authorizing your client in the OPEN API Administration tool, 
export the credentials and paste the contents of the export file below 
(making sure to include the final blank line). 
Then enter control-D to continue: 

>>>
Client Information

Name: Sample Client
Base URL: https://xxxx-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx.luna.akamaiapis.net/

Access Tokens:

    akab-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx


Client Credentials:

    Client token: akab-xxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxx     Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxx+xxxxxxxxxxxxxx=


<<<


The section 'default' has been succesfully added to /Users/ktyacke/.edgerc
``` 

When you run `gen_edgerc` with no command line options, the script will create a file named '.edgerc' in the current users home directory and add a section titled 'default' to the file. 

The only sample script that references the 'default' section is diagnostic_tools.js. For all other examples you will need to add a section corresponding to the sectionName property in the script to the .edgerc file. 

For example: Before running the billing-usage script, you would first open billing-usage.js and find that the value of sectionName is 'billingusage'. You would then add a 'billingusage' section to your .edgerc file as follows:

```bash
$ gen_edgerc --section billingusage
```

## Debug
All of the sample code in the src directory also support the --debug to see all of the HTTP traffic.  These flags can help enormously in figuring out what's going wrong or how it's working. Try it out for yourself:

``` bash
$ node src/diagnostic_tools.js --debug
```

## Diagnostic Tools
The first, and most simple, example is diagnostic-tools.js. This script will use the 'default' credentials that were created while following the [Authorizing Your Client](https://developer.akamai.com/introduction/Prov_Creds.html) instruction. If you have not yet done this, please go back to the beginning of this README and follow those instructions before continuing. The 'default' credentials created in the previous step give you permission to run the "dig" command from the API.

``` bash
$ node src/diagnostic_tools.js
```

This simple script runs the 'locations' call to find out where the Akamai servers are located. The API can run the 'dig' for you from any of these locations, so once the locations are returned, it grabs one at random and makes the dig call from there.

By reviewing the code you can see how simple it is to make API calls.



## Content Control Utility (CCU)
The Content Control Utility (CCU) allows you to purge Edge content by request. 
The example first makes a GET request to `/ccu/v2/queues/default` to retrieve the
number of items currently in the default purge queue. Next it makes a POST 
request to `/ccu/v2/queues/default` to add a new item to the default purge queue.
Finally, using the progressUri value that is returned from the POST request, it
checks the status of the purge for the item that was added in the second step.

```bash
$ node src/ccu.js
```


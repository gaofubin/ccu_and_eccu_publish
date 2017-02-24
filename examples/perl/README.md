# Perl Code Examples

This will guide you through the steps necessary to set up credentials and start playing with the sample code.  Note that once you've set up credentials for one language, you don't need to re-create them for another language.  If you set up the credentials for perl, python and php will use the same credentials.

These instructions expect that you are in the examples/perl subdirectory of the github repository.  To grab the appropriate libraries from cpan:
```bash
$ cpan -i Akamai::Edgegrid
```

# Authentication and Provisioning
The easiest way to walk through the needed provisioning and authentication to get your credentials is by following the instructions on [Authorizing your Client](https://developer.akamai.com/introduction/Prov_Creds.html) from the Getting started guide on our site.  Once you have done this, you'll be able to run the 'diagnostic tools' example scripts.

## Credential File Creation
You can get your credentials set up for use by the sample code by using the gen_edgerc.pl command in this directory:
```bash
$ perl gen_edgerc.pl
``` 

When you run gen_edgerc.py with no command line options, the script will create a 'default' section in your ~/.edgerc file.  For examples other than diagnostic_tools.py you'll need to pass the name of the appropriate section as an
argument, for example this is how you'd set up ccu.pl:
```bash
perl gen_edgerc.pl -s ccu
```

You can find the correct name for the credentials section on the "section=" line in the example script.  If you run the script again for a specific section (including 'default') it will overwrite the previous credentials with your new ones.

## Diagnostic Tools - diagnostic_tools.pl
The first example code to test is the diagnostic_tools.py script.  The credentials from the creation step give you permission to run the "dig" command from the API.

``` bash
./diagnostic_tools.pl
```

This simple script runs the 'locations' call to find out where the Akamai servers are located.  The API can run the 'dig' for you from any of these locations.  Once it has done that, it grabs one at random and makes the dig call from there.

By reviewing the code you can see how simple it is to make API calls.

All of the sample code in the directory also supports --verbose to see the output on the screen, and/or --debug to see all of the HTTP traffic.  These flags can help enormously in figuring out what's going wrong or how it's working.

``` bash
./diagnostic_tools.pl --verbose
./diagnostic_tools.pl --debug
```

## CCU (Purge) - ccu.pl
We have a [blog post](https://community.akamai.com/community/developer/blog/2015/08/19/getting-started-with-the-v2-open-ccu-api?sr=stream) with instructions on getting set up with the CCU API.
Prerequisites: ccu credentials and edit the filename to a valid file on your system


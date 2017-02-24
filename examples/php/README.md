# Akamai {OPEN} PHP Kickstart

> **Note:** All commands are to be run in the same directory as this README

## Installation

No installation is necessary for these examples, they will automatically install all required dependencies using `composer` on first run.

## How To

The easiest way to walk through the needed provisioning and authentication to get your credentials is under "provisioning" in the Getting started guide on our site:
https://developer.akamai.com/introduction/index.html

### Credentials

You can get your credentials set up by using the `gen_edgerc.php` command:

```bash
$ ./gen_edgerc.php
``` 

## Example: Diagnostic tools

For examples other than diagnostic_tools you'll want to pass the name of the appropriate section as an argument, for example this is how you'd set up ccu.py:

```bash
$ gen_edgerc.php ccu
$ ./ccu.php
```

## Debugging

To debug this library, you can turn on debugging, and verbose modes, either together or separately by passing in one or both of the appropriate flags:

```bash
$ ./diagnostic_tools.php --verbose --debug
```

The `--verbose` mode will automatically display all responses, while `--debug` will show the raw HTTP request and response headers.

## Using the library

For more information on using the library, please refer to the [library README](https://github.com/akamai-open/edgegrid-auth-php/blob/master/README.md).
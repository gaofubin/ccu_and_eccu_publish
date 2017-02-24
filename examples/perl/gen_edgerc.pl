#! /usr/bin/env perl

# This script will generate a ~/.edgerc credentials file based on
# the output of the "{OPEN} API Administration" tool in Luna Control Center.
#
# Usage: perl gen_edgerc_new.pl -s <section_name> -f <export_file>


use Getopt::Long;
use Config::IniFiles;
use File::HomeDir;

$fileSpec = File::HomeDir->my_home . "/.edgerc";

GetOptions ('section=s' => \$config_section,
            'file=s' => \$cred_file);

# Determine the section name giving precedence to -s value
$section_name = $config_section || "default";

print "Akamai OPEN API EdgeGrid Credentials\n\n";
print "This script will create a $section_name section in the local ~/.edgerc credential file.\n";

if ($cred_file) {
	print "+++ Reading from EdgeGrid credentials file: $cred_file\n";
    open(my $fh, '<:encoding(UTF-8)', $cred_file)
        or die "Could not open file '$cred_file' $!";
    @text = <$fh>;

} else {
	print "After authorizing your client in the {OPEN} API Administration tool,\n";
	print "export the credentials and paste the contents of the export file below,\n";
	print "followed by control-D.\n\n";
	print ">>>\n";
	@text = <STDIN>;
}

my $cfg = Config::IniFiles->new( -file => $fileSpec ) or die "Can't read file\n";

foreach my $line (@text) {
    chomp($line);
    next unless ($line =~ /=/);
    ($field, $value) = ($line =~ /^(.*) = (.*)$/);
    if ($cfg and $cfg->exists($section_name, $field)) {
        $cfg->setval($section_name, $field, $value);
    } else {
        $cfg->newval($section_name, $field, $value) or die "Can't set new val\n";
    }
}

$cfg->WriteConfig($fileSpec);

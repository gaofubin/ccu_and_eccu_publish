<?php
$colors = getColors();
extract($colors);

if (!file_exists(__DIR__ . '/../vendor/autoload.php')) {
    if (!in_array('--yes', $_SERVER['argv'])) {
        echo "{$yellow}You must first run \"{$cyan}composer.phar install${yellow}\" inside this directory to run this script.${reset}\n";
        echo "Would you like to run it now? [{$green}Y{$reset}/{$red}n{$reset}] ";
        while ($input = fgets(STDIN)) {
            $input = trim($input);
            if (strtolower($input) == 'y' || empty($input)) {
                installComposer();
            } else {
                echo "\n{$red}This script will now exit.{$reset}\n";
                exit;
            }
            break;
        }
    } else {
        installComposer();
    }
} else {
    require_once __DIR__  . '/../vendor/autoload.php';
}

function installComposer()
{
    $colors = getColors();
    extract($colors);

    $quiet = '';
    if (!in_array('--debug', $_SERVER['argv'])) {
        $quiet = '-q';
        echo "\n{$yellow}Running composer... {$reset}";
    }
    $rundir = __DIR__ . '/../';
    echo `cd "$rundir" && php composer.phar update $quiet`;
    if (file_exists(__DIR__ . '/../vendor/autoload.php')) {
        require_once __DIR__  . '/../vendor/autoload.php';
        if ($quiet) {
            echo "[{$green}OK{$reset}]\n\n";
        } else {
            echo "\n\n";
        }
    } else {
        if ($quiet) {
            echo "[{$red}!!{$reset}]\n";
            echo "{$red}Something went wrong! Please try again using the \"--debug\" flag :({$reset}\n";
        } else {
            echo "{$red}Something went wrong! Please check the output above for details.{$reset}\n";
        }
        exit;
    }
}

function getColors()
{
    return [
        'red' => "\x1b[31;01m",
        'yellow' => "\x1b[33;01m",
        'green' => "\x1b[32;01m",
        'blue' => "\x1b[34;01m",
        'magenta' => "\x1b[35;01m",
        'cyan' => "\x1b[36;01m",
        'reset' => "\x1b[39;49;00m",
    ];
}

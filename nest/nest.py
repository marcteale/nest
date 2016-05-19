#!~/nest/bin/python3.4

import argparse
import configparser
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)


def get_config():
    '''Looks for command line args and config file.  Returns a dict of validated
    options.'''
    cli_flags = get_config_from_cli()
    file_config = get_config_from_file(cli_flags['config'])
    config_merged = validate_config(cli_flags, file_config)
    return config_merged


def get_config_from_cli():
    '''Gets configuration from the command line args.  Returns a dict of
    options.'''
    parser = argparse.ArgumentParser(
        description='Query the Nest API and return output in the requested format.')
    parser.add_argument(
        '--username', '-u',
        type=str,
        help='Nest API username')
    parser.add_argument(
        '--password', '-p',
        type=str,
        help="Nest API password")
    parser.add_argument(
        '--scale', '-s',
        type=str,
        default='c',
        choices=['c', 'f', 'k'],
        help="Temperature scale.  Default: Celsius")
    parser.add_argument(
        '--format', '-f',
        type=str,
        default='observium',
        choices=['json', 'csv', 'observium'],
        help="Output format.  Default: observium")
    parser.add_argument(
        '-config', '-c',
        type=str,
        default='nest.conf',
        help="Configuration file.  Default: nest.conf.")
    parser.add_argument(
        '--outfile', '-o',
        type=str,
        default=None,
        help="Output file.  Defaults to stdout.")
    print('cli flags')
    pp.pprint(vars(parser.parse_args()))
    return vars(parser.parse_args())


def get_config_from_file(file_config):
    '''Gets configuration from the specified configuration file.  Returns a dict
    of the parsed file.'''
    config = configparser.ConfigParser()

    try:
        config.read(file_config)
        print('file_config values:')
        pp.pprint(vars(config)['_sections']['nest'])
        return vars(config)['_sections']['nest']
    except:
        sys.exit("Error reading configuration file.  Does it exist?")


def validate_config(cli_flags, file_config):
    '''Validates the file and CLI configs fetched by get_config.  If there are
    conflicts between cli_flags and file_config, options in cli_flags take
    precedence.  Exits uncleanly if invalid configuration is specified.

    Takes two dicts.  Returns the merged dict.'''
    merged = {}

    print('\nmerged values:')
    for key in cli_flags:
            if cli_flags[key] is not None:
                merged[key] = cli_flags[key]
            elif key in file_config:
                merged[key] = file_config[key]
    if 'username' not in merged:
        sys.exit("No username specified!")
    if 'password' not in merged:
        sys.exit("No password specified!")
    pp.pprint(merged)
    return cli_flags


def login():
    '''Log in to the Nest API and get some kind of token or some shit.'''
    pass


def fetch_data():
    '''Get the requested data from the Nest API.'''
    pass


def output_data():
    '''Output the data in the requested format.'''
    pass


if __name__ == '__main__':
    get_config()
    login()
    fetch_data()
    output_data()

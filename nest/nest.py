#!~/nest/bin/python3.4

import argparse
import configparser
import os.path
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)


def get_config():
    '''Looks for command line args and config file.  Returns a dict of validated
    options.'''
    config_cli = get_config_from_cli()
    config_file = get_config_from_file(config_cli['file'])
    config_merged = validate_config(config_cli, config_file)
    return config_cli


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
        help="Temperature scale.")
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='observium',
        choices=['json', 'csv', 'observium', 'rrdtool'])
    parser.add_argument(
        '--file', '-f',
        type=str,
        default='nest.conf',
        help="Configuration file.  Defaults to nest.conf.")
    print('cli flags')
    pp.pprint(vars(parser.parse_args()))
    return vars(parser.parse_args())


def get_config_from_file(config_file):
    '''Gets configuration from the specified configuration file.  Returns a dict
    of the parsed file.'''
    if os.path.isfile(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        print('config_file values:')
        pp.pprint(vars(config)['_sections']['nest'])
        return vars(config)['_sections']['nest']
    else:
        sys.exit("Non-existent configuration file specified.")


def validate_config(config_cli, config_file):
    '''Validates the file and CLI configs fetched by get_config.  If there are
    conflicts between config_cli and config_file, options in config_cli take
    precedence.  Exits uncleanly if invalid configuration is specified.

    Takes two dicts.  Returns the merged dict.'''
    return config_cli


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

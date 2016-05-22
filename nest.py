#!/usr/bin/python

import argparse
import configparser
import sys


def get_config():
    '''Looks for command line args and config file.  Returns a dict of validated
    options.'''

    cli_flags = get_config_from_cli()
    file_config = get_config_from_file(cli_flags['config'])
    config_merged = validate_config(cli_flags, file_config)
    return config_merged


def get_config_from_cli():
    '''Gets configuration from the command line args.  Returns a dict of
    options.

    TODO: The help doesn't print because of how this is called.'''
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
    return vars(parser.parse_args())


def get_config_from_file(file_config):
    '''Gets configuration from the specified configuration file.  Returns a dict
    of the parsed file.'''
    config = configparser.ConfigParser()

    try:
        config.read(file_config)
        return vars(config)['_sections']['nest']
    except:
        sys.exit("Error reading configuration file.  Does it exist?")


def validate_config(cli_flags, file_config):
    '''Validates the file and CLI configs fetched by get_config.  If there are
    conflicts between cli_flags and file_config, options in cli_flags take
    precedence.  Exits uncleanly if invalid configuration is specified.

    Takes two dicts.  Returns the merged dict.'''
    # TODO: The resulting dict contains unicode and ASCII.  It should be all one
    # or the other.

    merged = {}

    for key in cli_flags:
            if cli_flags[key] is not None:
                merged[key] = cli_flags[key]
            elif key in file_config:
                merged[key] = file_config[key]
    if 'username' not in merged:
        sys.exit("No username specified!")
    if 'password' not in merged:
        sys.exit("No password specified!")
    return cli_flags


def login():    # need to update fetch_data() when renaming this
    '''Load or generate long-term access token and store it at ~/.nest'''
    import os.path
    home_dir = os.path.expanduser('~') + '/'

    try:
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    except:
        import auth
        auth.create_tokenfile()
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    return(token)


def fetch_data():  # this needs to be fleshed out to include error checking.
    '''Get the requested data from the Nest API.'''
    import requests
    import json
    api_root = 'https://developer-api.nest.com/'
    token = login()

    response = requests.get(api_root + '?auth=' + token)

    api_json = json.loads(response.text)

    return(api_json['devices'])


def output_data():
    '''Output the data in the requested format.'''
    api_json = fetch_data()
    data = {}
    # loop through the json to flatten to dict with pipe-delimited keywords
    for device_type_key in api_json:
        for device_id_key in api_json[device_type_key]:
            for key in api_json[device_type_key][device_id_key]:
                data[device_type_key + '|' + device_id_key + '|' + key] = api_json[device_type_key][device_id_key][key]
    return(data)

if __name__ == '__main__':
    get_config()
    output_data()

#!/usr/bin/python

import argparse
import configparser
import json  # simplejson
import os.path
import requests
import sys
import uuid


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
    global conf
    config = configparser.ConfigParser()

    try:
        config.read(file_config)
        conf = vars(config)['_sections']['nest']
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
    # if 'username' not in merged:
    #     sys.exit("No username specified!")
    # if 'password' not in merged:
    #     sys.exit("No password specified!")
    return cli_flags


def get_pin():
    '''Make the user retrieve their temporary PIN from home.nest.com in order
    to establish the long-term token used for API calls.
    Returns user-input 8-digit temporary PIN.'''

    client_id = 'client_id=b1da9bf1-7e2a-49d4-8728-5d4a75349003'

    oauth_base_url = 'https://home.nest.com/login/oauth2?{}&state='.format(client_id)
    # generate a unique-ish 'state' value to protect against cross-site request
    # forgery attacks.
    # https://developers.nest.com/documentation/cloud/how-to-auth
    state = str(uuid.uuid4())

    print("\n\nLog in at the following URL:\n{}{}\n\n".format(oauth_base_url, state))
    pin = raw_input("Paste the PIN generated to continue setup: ")
    while len(pin) != 8:
        pin = raw_input("Invalid PIN.  Paste the PIN from nest.home.com to continue setup: ")
    return(pin)


def get_access_token():
    '''Generate and store the long-term token used for home.nest.com API calls.
    Returns acess token string 'c.123....' '''

    client_id = 'client_id=b1da9bf1-7e2a-49d4-8728-5d4a75349003'

    pin = get_pin()
    access_token_url = 'https://api.home.nest.com/oauth2/access_token?{}&code={}&client_secret=odIh0k73deLQbRHdNHgepDNPR&grant_type=authorization_code'.format(client_id, pin)

    response = requests.post(access_token_url)
    token_json = json.loads(response.text)

    return(token_json['access_token'])


def create_tokenfile():
    '''Creates ~/.nest token file for future use by API.'''

    home_dir = os.path.expanduser('~') + '/'

    # TODO: The token should be stored in the same location as nest.py.
    # TODO: Make sure the file actually contains a token.
    if os.path.isfile(home_dir + '.nest'):
        return('~./nest already exists! Please rename or delete this file before re-running.')
    else:
        with open(home_dir + '.nest', 'w+') as f:
            f.write(get_access_token())
        return('Successfully stored access token in ~/.nest')


def login():    # need to update fetch_data() when renaming this
    '''Load or generate long-term access token and store it at ~/.nest'''
    home_dir = os.path.expanduser('~') + '/'

    try:
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    except:
        create_tokenfile()
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    return(token)


def fetch_data():  # this needs to be fleshed out to include error checking.
    '''Get the requested data from the Nest API.'''
    api_root = 'https://developer-api.nest.com/'
    token = login()

    response = requests.get(api_root + '?auth=' + token)

    api_json = json.loads(response.text)

    return(api_json['devices'])


def output_data():
    '''Output the data in the requested format.'''
    api_json = fetch_data()
    data = []
    # loop through the json to flatten to tuple with pipe-delimited fields
    for device_type_key in api_json:
        for device_id_key in api_json[device_type_key]:
            for key in api_json[device_type_key][device_id_key]:
                data.append("{}|{}|{}|{}".format(device_type_key, device_id_key, key, api_json[device_type_key][device_id_key][key]))
                if conf['format'] == 'observium':  # create genericly-named temperature keys
                    if conf['scale'] == 'c':
                        if key[-2:] == '_c':
                            data.append("{}|{}|{}|{}".format(device_type_key, device_id_key, key[:-2], api_json[device_type_key][device_id_key][key]))
                    elif conf['scale'] == 'f':
                        if key[-2:] == '_f':
                            data.append("{}|{}|{}|{}".format(device_type_key, device_id_key, key[:-2], api_json[device_type_key][device_id_key][key]))
                    elif conf['scale'] == 'k':
                        if key[-2:] == '_c':
                            data.append("{}|{}|{}|{}".format(device_type_key, device_id_key, key[:-2], api_json[device_type_key][device_id_key][key] + 273.15))
    data.sort()
    return(data)


#if config['scale'] == 'k'


if __name__ == '__main__':
    get_config()
    print('<<<nest>>>')
    for line in output_data():
        print(line)

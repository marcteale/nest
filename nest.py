#!/usr/bin/python
import argparse
import configparser
import json  # simplejson
import os.path
import requests
import sys
import uuid
from pprint import pprint # NOQA


# TODO: Kill global variables.
# TODO: Add config file and CLI args stuff for observium output
observium = True
# TODO: Actually output to something other than STDOUT.
# TODO: Read from the config file specified at the command line.
# TODO: Read in client_id and pass it around as a parameter.


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

    # TODO: No error checking is done on the config file.
    merged = file_config

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

    # TODO: Read access token and client secret from config
    pin = get_pin()
    baseurl = 'https://api.home.nest.com/oauth2/'
    params = {
        'access_token': 'b1da9bf1-7e2a-49d4-8728-5d4a75349003',
        'client_secret': 'odIh0k73deLQbRHdNHgepDNPR',
        'grant_type': 'authorization_code',
        'code': pin,
    }

    response = requests.post(url=baseurl, params=params)
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


def login():    # need to update fetch_json() when renaming this
    '''Load or generate long-term access token and store it at ~/.nest'''
    # TODO: Store the token in nest.conf
    # TODO: Fail if no token is available
    home_dir = os.path.expanduser('~') + '/'

    try:
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    except:
        create_tokenfile()
        with open(home_dir + '.nest', 'r') as f:
            token = f.read()
    return(token)


def fetch_json():
    ''' Query the Nest API and return a json object. '''
    # TODO: include error checking.
    api_root = 'https://developer-api.nest.com/'
    token = login()
    params = {'auth': token}
    response = requests.get(url=api_root, params=params)

    api_json = json.loads(response.text)
    return(api_json)


def extract_zip(data):
    ''' Takes the API results, extracts and return the zip code.'''
    struct_id = data['structures'].keys()[0]
    zipcode = data['structures'][struct_id]['postal_code']
    return zipcode


def get_weather(zipcode, units='F'):
    ''' Takes a zip code and queries openweathermap.org.  Returns the
    temperature as a float.'''

    params = {
        'appid': '154497b64b6b3281f3843b597fe8ac55',
        'zip': zipcode,
        'units': units
    }

    baseurl = 'http://api.openweathermap.org/data/2.5/weather?'
    resp = requests.get(url=baseurl, params=params)
    return json.loads(resp.text)


def extract_units(data):
    ''' Takes the results of the Nest API and extracts the units of measurement
    used.  Returns 'metric' if 'C' and 'imperial if 'F'. '''
    try:
        therm_id = data['devices']['thermostats'].keys()[0]
    except KeyError:
        sys.exit('Error retrieving thermostat data.')

    units = data['devices']['thermostats'][therm_id]['temperature_scale']

    if units == 'C':
        return 'metric'
    else:
        return 'imperial'


if __name__ == '__main__':
    # Parse command line and config file options, and validate them.
    parser = argparse.ArgumentParser(
        description='Query the Nest API and return output in the requested format.')
    parser.add_argument(
        '--scale', '-s',
        type=str,
        default='c',
        choices=['c', 'f'],
        help="Temperature scale.  Default: Celsius")
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

    cli_flags = vars(parser.parse_args())
    file_config = get_config_from_file(cli_flags['config'])
    config_merged = validate_config(cli_flags, file_config)

    data = fetch_json()
    weather = get_weather(extract_zip(data), extract_units(data))

    if observium:
        print('<<<nest>>>')
    print json.dumps({'nest': data, 'weather': weather})

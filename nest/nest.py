#!/usr/bin/python

import argparse


def get_config():
    parser = argparse.ArgumentParser(description='Query the Nest API and return output in the requested format.')
    parser.add_argument('--username', '-u', help='Nest API username')
    parser.add_argument('--password', '-p', help="Nest API password")

    get_config_from_cli
    '''Look for command line args and config file.  If config is in both,
    command line args win.'''
    pass


def get_config_from_cli():
    '''Get configuration from the command line args.'''
    pass


def get_config_from_file():
    '''Get configuration from the specified configuration file.'''
    pass


def validate_config():
    '''Validate the configuration created by get_config, exit uncleanly if bad
    config is specified.'''
    pass


def login():
    '''Log in to the Nest API and get some kind of token or some shit.'''
    pass


def fetch_data():
    '''Get the requested data from the Nest API.'''
    pass


def output_data():
    '''Output the data in the requested format.'''
    pass


def __init__():
    get_config()
    validate_config()
    login()
    fetch_data
    output_data

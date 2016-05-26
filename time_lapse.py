#!/usr/bin/python

import os.path
import requests
import json
import time
import uuid
'''
notes:
API:
{devices{cameras{device_id{
    "image_url": "STRING1/device_id/STRING2?auth=access_token",
    "animated_image_url": "STRING1/device_id/STRING2?auth=access_token"
}}}}


'''
api_root = 'https://developer-api.nest.com/'


# load credentials from auth module

# build query for camera

def get_cameras():
    '''Retrieve list of camera device IDs and their friendly names'''
    home_dir = os.path.expanduser('~') + '/'
        
    with open(home_dir + '.nest', 'r') as f:
        token = f.read()
    cameras_list = []
    response = requests.get(api_root+'devices/cameras?auth='+token)
    cameras_json = json.loads(response.text)
    for camera in cameras_json:
        device_id = camera
        name = cameras_json[camera]['name']
        cameras_list.append((device_id,name))
    return(cameras_list)
#    return(cameras_list)


def get_image():
    token = login()
    device_id = get_cameras()[0][0]
    response = requests.get(api_root + 'devices/cameras/'+ device_id + '/last_event/image_url/?auth=' + token)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    path = '/home/bob/time_lapse/'
    with open(path + 'nest-' + timestr + '.jpg', 'wb+') as f:
        response_image = requests.get(response.text[1:-1], stream=True)
        for chunk in response_image.iter_content(1024):
            f.write(chunk)
    print('created '+ 'nest-' + timestr + '.jpg')


def get_pin():
    '''Make the user retrieve their temporary PIN from home.nest.com in order
    to establish the long-term token used for API calls.
    Returns user-input 8-digit temporary PIN.'''

    client_id = 'client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed'

    oauth_base_url = 'https://home.nest.com/login/oauth2?{}&state='.format(client_id)
    # generate a unique-ish 'state' value to protect against cross-site request
    # forgery attacks.
    # https://developers.nest.com/documentation/cloud/how-to-auth
    state = str(uuid.uuid4())

    print("\n\nLog in at the following URL:\n{}{}\n\n".format(oauth_base_url, state))
    pin = raw_input("Paste the PIN generated to continue setup: ")
    while len(pin) != 8:
        pin = input("Invalid PIN.  Paste the PIN from nest.home.com to continue setup: ")
    return(pin)


def get_access_token():
    '''Generate and store the long-term token used for home.nest.com API calls.
    Returns acess token string 'c.123....' '''

    client_id = 'client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed'

    pin = get_pin()
    access_token_url = 'https://api.home.nest.com/oauth2/access_token?{}&code={}&client_secret=6K4PzAUC3GsFhB0U5twr2P8If&grant_type=authorization_code'.format(client_id, pin)

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


def login():    # need to update fetch_json() when renaming this
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


if __name__ == '__main__':
    while True:
        try:
            get_image()
        except:
            pass
        time.sleep(60)

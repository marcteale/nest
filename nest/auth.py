#auth model:
#* setup.py should launch browser with link to accept terms & generate PIN
#* pull pin & use to generate long-term token
#* store long-term token for later/scheduled calls

import webbrowser
import uuid
import requests
import json
import os.path

def get_pin():
    '''Make the user retrieve their temporary pincode from home.nest.com in order
    to establish the long-term token used for API calls.
    Returns user-input 8-digit temporary pincode.'''

    oauth_base_url = 'https://home.nest.com/login/oauth2?client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed&state='
    state = str(uuid.uuid4()) # generate a unique-ish 'state' value to protect against cross-site request forgery attacks.
                              # per https://developers.nest.com/documentation/cloud/how-to-auth '''
    webbrowser.open(oauth_base_url + state) # add some error checking.  https://docs.python.org/3/library/webbrowser.html#webbrowser.Error

    pin = input("Paste the pincode from nest.home.com to continue the setup:  ")
    while len(pin) != 8:
        pin = input("Invalid pincode.  Paste the pincode from nest.home.com to continue the setup:  ")
    return(pin)

def get_access_token():
    '''Generate and store the long-term token used for home.nest.com API calls.
    Returns acess token string 'c.123....' '''

    pin = get_pin()
    access_token_url = 'https://api.home.nest.com/oauth2/access_token?client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed&code='+pin+'&client_secret=6K4PzAUC3GsFhB0U5twr2P8If&grant_type=authorization_code'

    response = requests.post(access_token_url)
    token_json = json.loads(response.text)

    return(token_json['access_token'])

def create_tokenfile():
    '''Creates ~/.nest token file for futre use by api.'''

    home_dir = os.path.expanduser('~') + '/'

    if os.path.isfile(home_dir + '.nest'):
        return('~./nest already exists! Please rename or delete this file before re-running.')
    else:
        with open(home_dir + '.nest','w+') as f:
            f.write(get_access_token())
        return('Successfully stored access token in ~/.nest')

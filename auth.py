# TODO: We're requesting way, way more permissions that we want or need.

# auth model:
# * setup.py should launch browser with link to accept terms & generate PIN
# * pull pin & use to generate long-term token
# * store long-term token for later/scheduled calls

import uuid
import requests
import json
import os.path

client_id = 'client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed'


def get_pin():
    '''Make the user retrieve their temporary pincode from home.nest.com in order
    to establish the long-term token used for API calls.
    Returns user-input 8-digit temporary pincode.'''

    # oauth_base_url = 'https://home.nest.com/login/oauth2?client_id=e8042a21-e70e-49a6-8430-3fe17fcea7ed&state='
    oauth_base_url = 'https://home.nest.com/login/oauth2?{}&state='.format(client_id)
    # generate a unique-ish 'state' value to protect against cross-site request
    # forgery attacks.
    # https://developers.nest.com/documentation/cloud/how-to-auth
    state = str(uuid.uuid4())

    print("\n\nLog in at the following URL:\n{}{}\n\n".format(oauth_base_url, state))
    pin = raw_input("Paste the PIN generated to continue setup: ")
    while len(pin) != 8:
        pin = raw_input("Invalid pincode.  Paste the PIN from nest.home.com to continue setup: ")
    return(pin)


def get_access_token():
    '''Generate and store the long-term token used for home.nest.com API calls.
    Returns acess token string 'c.123....' '''

    pin = get_pin()
    access_token_url = 'https://api.home.nest.com/oauth2/access_token?{0}&code='+pin+'&client_secret=6K4PzAUC3GsFhB0U5twr2P8If&grant_type=authorization_code'.format(client_id)

    response = requests.post(access_token_url)
    token_json = json.loads(response.text)

    return(token_json['access_token'])


def create_tokenfile():
    '''Creates ~/.nest token file for future use by API.'''

    home_dir = os.path.expanduser('~') + '/'

    # TODO: The PIN should be stored in the same location as nest.py.
    # TODO: Make sure the file actually contains a PIN.
    if os.path.isfile(home_dir + '.nest'):
        return('~./nest already exists! Please rename or delete this file before re-running.')
    else:
        with open(home_dir + '.nest', 'w+') as f:
            f.write(get_access_token())
        return('Successfully stored access token in ~/.nest')

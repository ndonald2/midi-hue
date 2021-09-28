import json
import os
import requests as req

CREDENTIALS_PATH = '.credentials'
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'
GROUP_ID = 2

def discover_ip():
    r = req.get(DISCOVERY_URI)
    return r.json()[0].get('internalipaddress')

def create_user(bridge_ip):
    if os.path.exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH,'r') as file:
            data = json.load(file)
            return (data['username'], data['clientkey'])

    uri = f'http://{bridge_ip}/api'
    r = req.post(uri, json={'devicetype': DEVICETYPE, 'generateclientkey': True})
    if r.status_code != 200:
        print(f'An error occurred: HTTP Status {r.status_code}')
        return (None, None)
    else:
        obj = r.json()[0]
        success = obj.get('success')
        error = obj.get('error')
        if error != None:
            if error.get('type') == 101:
                print('Push button on Hue Bridge and try again')
            else:
                print('An error occurred')
            return (None, None)

        # Write JSON
        with open(CREDENTIALS_PATH, 'w') as file:
            json.dump(success, file) 

        username = success.get('username')
        clientkey = success.get('clientkey')
        return (username, clientkey)

bridge_ip = discover_ip()
username, clientkey = create_user(bridge_ip)

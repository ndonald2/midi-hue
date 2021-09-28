import os
import json
import requests

CREDENTIALS_PATH = os.path.expanduser('~/.midihue')
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'

class HueClient:

    def __init__(self, bridge_ip=None):
        self._bridge_ip = bridge_ip
        self._username = None
        self._clientkey = None
        self._find_or_create_user()

    @property
    def bridge_ip(self):
        if self._bridge_ip != None:
            return self._bridge_ip
        req = requests.get(DISCOVERY_URI)
        self._bridge_ip = req.json()[0].get('internalipaddress')
        return self._bridge_ip

    @property
    def username(self):
        return self._username

    @property
    def clientkey(self):
        return self._clientkey

    def reset(self):
        self._username = None
        self._clientkey = None
        self._find_or_create_user()

    # Private

    def _find_or_create_user(self):
        if self._read_credentials():
            return

        # Else need to create an authorized user with API
        uri = f'http://{self.bridge_ip}/api'
        body = {'devicetype': DEVICETYPE, 'generateclientkey': True}
        req = requests.post(uri, json=body)
        response = req.json()[0]

        try:
            success = response['success']
            self._write_credentials(success)
            self._username = success['username']
            self._clientkey = success['clientkey']
        except KeyError:
            (errtype, errdesc) = self._error_info(response)
            if errtype == 101:
                print('Please press the button on the Hue bridge and try again')
            else:
                print(f'[HueClient] failed to create user: ({errtype} – {errdesc})')

    def _read_credentials(self):
        try:
            with open(CREDENTIALS_PATH,'r') as file:
                data = json.load(file)
                self._username = data['username']
                self._clientkey = data['clientkey']
                return True
        except FileNotFoundError:
            return False

    def _write_credentials(self, content):
        with open(CREDENTIALS_PATH, 'w+') as file:
            json.dump(content, file)

    def _error_info(self, response):
        error = response.get('error')
        return (error.get('type'), error.get('description'))

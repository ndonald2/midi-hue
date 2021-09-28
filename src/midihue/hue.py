import os
import json
import requests

CREDENTIALS_PATH = '~/.midihue'
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'

class HueClient:

    def __init__(self):
        self._bridge_ip = None

    @property
    def bridge_ip(self):
        if self._bridge_ip != None:
            return self._bridge_ip
        req = requests.get(DISCOVERY_URI)
        self._bridge_ip = req.json()[0].get('internalipaddress')
        return self._bridge_ip

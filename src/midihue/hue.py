import os
import json
import socket
import requests
from mbedtls import tls

CREDENTIALS_PATH = os.path.expanduser('~/.midihue')
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'


class HueClientError(Exception):
    pass


class HueClient:

    def __init__(self, bridge_ip=None):
        self._bridge_ip = bridge_ip
        self._username = None
        self._clientkey = None
        self._find_or_create_user()

    @property
    def bridge_ip(self):
        if self._bridge_ip is not None:
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

    def set_stream_mode(self, group_id, active):
        uri = f'http://{self.bridge_ip}/api/{self.username}/groups/{group_id}'
        req = requests.put(uri, json={'stream': {'active': active}})
        response = req.json()[0]
        if 'error' in response:
            raise HueClientError(
                'Failed to activate stream mode: ({errtype} – {errdesc})'
            )

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
                print('Please press the button on the ' +
                      'Hue bridge and try again')
            else:
                raise HueClientError(
                    'Failed to create user: ({errtype} – {errdesc})'
                )

    def _read_credentials(self):
        try:
            with open(CREDENTIALS_PATH, 'r') as file:
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


class HueStream:

    def __init__(self, group_id, client):
        self.group_id = group_id
        self.client = client
        self._socket = None

    def start(self):
        self.client.set_stream_mode(self.group_id, True)
        self._connect()

    def stop(self):
        self.client.set_stream_mode(self.group_id, False)
        self._disconnect()

    def send(self, dgram):
        assert self._socket is not None, \
            'Must start stream before sending data'
        self._socket.send(dgram)

    # Private

    def _connect(self):
        if self._socket is not None:
            self._disconnect()

        cli_conf = tls.DTLSConfiguration(
            pre_shared_key=(
                self.client.username,
                bytes.fromhex(self.client.clientkey)
            )
        )
        cli_ctx = tls.ClientContext(cli_conf)
        dtls_cli = cli_ctx.wrap_socket(
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
            server_hostname=None
        )

        dtls_cli.connect((self.client.bridge_ip, 2100))
        print('[HueStream] Socket connected, starting DTLS handshake...')

        handshook = False
        handshake_tries = 0
        while handshake_tries < 3:
            try:
                dtls_cli.do_handshake()
            except tls.WantReadError:
                handshake_tries += 1
                continue
            handshook = True
            break

        if handshook:
            print('[HueStream] DTLS handshake succeeded')
        else:
            print('[HueStream] DTLS handshake failed')

        self._socket = dtls_cli

    def _disconnect(self):
        self._socket.close()
        self._socket = None

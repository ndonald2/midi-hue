import os
import json
import socket
import requests
from mbedtls import tls

DEFAULT_CREDENTIALS_PATH = '~/.midihue'
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'


class HueClientError(Exception):
    pass


class HueClient:

    def __init__(self,
                 credentials_path=DEFAULT_CREDENTIALS_PATH,
                 bridge_ip=None):
        self._credentials_path = os.path.expanduser(credentials_path)
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

    def get_entertainment_groups(self):
        """Returns an array of available entertainment groups in the format
        of a tuple: (id, description)
        """
        uri = f'{self._base_uri}/groups'
        req = requests.get(uri)
        groups = []
        for gid, info in req.json().items():
            if info['type'] == 'Entertainment':
                name = info['name']
                n_lights = len(info['lights'])
                groups.append((gid, f'{name} ({n_lights} lights)'))
        return groups

    def set_stream_mode(self, group_id, active):
        uri = f'{self._base_uri}/groups/{group_id}'
        req = requests.put(uri, json={'stream': {'active': active}})
        response = req.json()[0]
        if 'error' in response:
            errtype, errdesc = self._error_info(response)
            raise HueClientError(
                f'Failed to activate stream mode: ({errtype} – {errdesc})'
            )

    def reset(self):
        self._username = None
        self._clientkey = None
        self._find_or_create_user()

    # Private

    @property
    def _base_uri(self):
        return f'http://{self.bridge_ip}/api/{self.username}'

    def _find_or_create_user(self):
        if self._read_credentials():
            return

        # Else need to create an authorized user with API
        print(self.bridge_ip)
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
                exit(1)
            else:
                raise HueClientError(
                    f'Failed to create user: ({errtype} – {errdesc})'
                )

    def _read_credentials(self):
        try:
            with open(self._credentials_path, 'r') as file:
                data = json.load(file)
                self._username = data['username']
                self._clientkey = data['clientkey']
                return True
        except json.decoder.JSONDecodeError:
            return False
        except FileNotFoundError:
            return False
        except KeyError:
            return False

    def _write_credentials(self, content):
        with open(self._credentials_path, 'w+') as file:
            json.dump(content, file)

    def _error_info(self, response):
        error = response.get('error')
        return (error.get('type'), error.get('description'))


class HueStream:

    class Message:

        # 1. Protocol (must be 'HueStream')
        # 2. Stream API version (1.0) - 2 bytes
        # 3. Sequence ID (ignored) - 1 Byte
        # 4. Reserved (must be 0) - 2 bytes
        # 5. Color space (RGB) - 1 byte
        # 6. Reserved (must be 0) 1 byte
        _HEADER = \
            b'HueStream' + \
            b'\x01\x00' + \
            b'\x00' + \
            b'\x00\x00' + \
            b'\x00' + \
            b'\x00'

        def __init__(self):
            self._lightdata = {}

        @property
        def bytes(self):
            b = self._HEADER
            for light_id, rgb in self._lightdata.items():
                b += b'\x00' + light_id.to_bytes(2, byteorder='big')
                b += rgb[0].to_bytes(2, byteorder='big')
                b += rgb[1].to_bytes(2, byteorder='big')
                b += rgb[2].to_bytes(2, byteorder='big')
            return b

        def add(self, light_id, rgb):
            assert len(rgb) == 3
            self._lightdata[int(light_id)] = rgb

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

    def send(self, message):
        assert self._socket is not None, \
            'Must start stream before sending data'
        self._socket.send(message.bytes)

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
        if self._socket is not None:
            self._socket.close()
            self._socket = None

import json
import os
import requests as req
import socket
from mbedtls import tls

CREDENTIALS_PATH = '.credentials'
DISCOVERY_URI = 'https://discovery.meethue.com'
DEVICETYPE = 'midi-hue'
GROUP_ID = 2

## REST API

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

def set_streaming_active(bridge_ip, username, group_id, active):
    uri = f'http://{bridge_ip}/api/{username}/groups/{group_id}'
    r = req.put(uri, json={'stream':{'active':active}})
    print(r.json())

## DTLS / SOCKET
def connect_dtls(hostname, username, secret):
    cli_conf = tls.DTLSConfiguration(
        pre_shared_key=(username, bytes.fromhex(secret))
    )
    cli_ctx = tls.ClientContext(cli_conf)
    dtls_cli = cli_ctx.wrap_socket(
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM),
        server_hostname=None
    )

    dtls_cli.connect((hostname,2100))
    print('connected')

    handshook = False
    handshake_tries = 0
    while handshake_tries < 3:
        try:
            dtls_cli.do_handshake()
        except tls.WantReadError:
            handshake_tries +=1 
            continue
        handshook = True
        break

    if handshook:
        print('Handshook!')
    else:
        print('Failed to handshake')

bridge_ip = discover_ip()
username, clientkey = create_user(bridge_ip)
if username is None:
    exit(1)
set_streaming_active(bridge_ip, username, GROUP_ID, True)
connect_dtls(bridge_ip, username, clientkey)

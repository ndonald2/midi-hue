import pytest
import json
from midihue.hue import HueClient, HueStream, DISCOVERY_URI


@pytest.fixture
def bridge_ip():
    return '123.456.789.23'


@pytest.fixture
def username():
    return 'asdoiga-weg-se9gseglksjg'


@pytest.fixture
def clientkey():
    return '0aw9gzx0asadg-saegase08g9'


@pytest.fixture
def creds_path():
    return '/tmp/huecreds'


@pytest.fixture
def mock_api(bridge_ip, username, clientkey, requests_mock):
    requests_mock.get(DISCOVERY_URI,
                      json=[{'internalipaddress': bridge_ip}])
    requests_mock.post(f'http://{bridge_ip}/api',
                       json=[{
                           'success': {
                               'username': username,
                               'clientkey': clientkey
                            }}])


@pytest.mark.usefixtures('client', 'bridge_ip', 'mock_api')
class TestHueClient:

    @pytest.fixture
    def mock_open(self, mocker):
        mopen = mocker.patch('builtins.open', mocker.mock_open())
        return mopen

    @pytest.fixture
    def mock_open_auth(self, mocker, username, clientkey):
        data = json.dumps({'username': username, 'clientkey': clientkey})
        mopen = mocker.patch('builtins.open', mocker.mock_open(read_data=data))
        return mopen

    @pytest.fixture
    def client(self, creds_path, mock_api, mock_open):
        return HueClient(credentials_path=creds_path)

    @pytest.fixture
    def client_auth(self, creds_path, mock_api, mock_open_auth):
        return HueClient(credentials_path=creds_path)

    def test_override_bridge_ip(self, mock_open_auth):
        assert HueClient(bridge_ip='127.0.0.1').bridge_ip == '127.0.0.1'

    def test_fetch_bridge_ip(self, client, bridge_ip):
        assert client.bridge_ip == bridge_ip

    def test_cache_bridge_ip(self, client, bridge_ip, requests_mock):
        # Access once to fetch/cache
        client.bridge_ip
        requests_mock.get(DISCOVERY_URI,
                          json=[{'internalipaddress': '0.0.0.0'}])
        assert client.bridge_ip == bridge_ip

    def test_create_user(self, client, mock_open,
                         creds_path, username, clientkey):
        mock_open.assert_any_call(creds_path, 'r')
        mock_open.assert_any_call(creds_path, 'w+')
        assert client.username == username
        assert client.clientkey == clientkey

    def test_load_user(self, client_auth, mock_open_auth,
                       creds_path, username, clientkey):
        # should be last call - no call to write
        mock_open_auth.assert_called_with(creds_path, 'r')
        assert client_auth.username == username
        assert client_auth.clientkey == clientkey


class TestHueStreamMessage:

    @pytest.fixture
    def header(self):
        return HueStream.Message._HEADER

    def test_header_protocolname(self, header):
        assert header.startswith(b'HueStream')

    def test_header_apiversion(self, header):
        assert header[9:11] == b'\x01\x00'

    @pytest.fixture
    def message(self):
        return HueStream.Message()

    def test_message_startswith_header(self, message, header):
        assert message.bytes.startswith(header)

    def test_message_single_light(self, message):
        message.add(5, (9865, 2048, 29398))
        assert message.bytes[-9:-6] == b'\x00\x00\x05'
        assert message.bytes[-6:] == b'\x26\x89\x08\x00\x72\xd6'

    def test_message_multi_lights(self, message):
        message.add(23, (9993, 2048, 29398))
        message.add(9, (16, 255, 16385))
        assert message.bytes[-18:-15] == b'\x00\x00\x17'
        assert message.bytes[-15:-9] == b'\x27\x09\x08\x00\x72\xd6'
        assert message.bytes[-9:-6] == b'\x00\x00\x09'
        assert message.bytes[-6:] == b'\x00\x10\x00\xff\x40\x01'

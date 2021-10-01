import pytest
import json
from midihue.hue import HueClient, HueStream, DISCOVERY_URI


class TestHueClient:

    @pytest.fixture(scope='module')
    def bridge_ip(self):
        return '123.456.789.23'

    @pytest.fixture(scope='module')
    def username(self):
        return 'asdoiga-weg-se9gseglksjg'

    @pytest.fixture(scope='module')
    def clientkey(self):
        return '0aw9gzx0asadg-saegase08g9'

    @pytest.fixture(scope='module')
    def creds_path(self):
        return '/tmp/huecreds'

    @pytest.fixture
    def mock_open(self, mocker):
        mopen = mocker.patch('builtins.open', mocker.mock_open())
        return mopen

    @pytest.fixture
    def mock_open_auth(self, mocker, username, clientkey):
        data = json.dumps({'username': username, 'clientkey': clientkey})
        mopen = mocker.patch('builtins.open', mocker.mock_open(read_data=data))
        return mopen

    @pytest.fixture(autouse=True)
    def mock_discovery(self, bridge_ip, requests_mock):
        requests_mock.get(DISCOVERY_URI,
                          json=[{'internalipaddress': bridge_ip}])

    @pytest.fixture(autouse=True)
    def mock_create_user(self, bridge_ip, username, clientkey, requests_mock):
        requests_mock.post(f'http://{bridge_ip}/api',
                           json=[{
                               'success': {
                                   'username': username,
                                   'clientkey': clientkey
                               }
                           }])

    @pytest.fixture
    def client(self, creds_path, mock_discovery, mock_create_user, mock_open):
        return HueClient(credentials_path=creds_path)

    @pytest.fixture
    def client_auth(self, creds_path, mock_discovery,
                    mock_create_user, mock_open_auth):
        return HueClient(credentials_path=creds_path)

    def test_override_bridge_ip(self, mock_open_auth):
        assert HueClient(bridge_ip='127.0.0.1').bridge_ip == '127.0.0.1'

    def test_fetch_bridge_ip(self, client_auth, bridge_ip, requests_mock):
        assert client_auth.bridge_ip == bridge_ip
        assert requests_mock.call_count == 1

    def test_cache_bridge_ip(self, client, bridge_ip, requests_mock):
        # Access once to fetch/cache
        client.bridge_ip
        requests_mock.get(DISCOVERY_URI,
                          json=[{'internalipaddress': '0.0.0.0'}])
        assert client.bridge_ip == bridge_ip

    def test_create_user(self, client, mock_open, requests_mock,
                         creds_path, username, clientkey):

        mock_open.assert_any_call(creds_path, 'r')
        mock_open.assert_any_call(creds_path, 'w+')

        # One to fetch bridge ip, one to create user
        assert requests_mock.call_count == 2

        last_req = requests_mock.request_history[-1]
        assert last_req.method == 'POST'
        assert last_req.url.endswith('/api')

        assert client.username == username
        assert client.clientkey == clientkey

    def test_load_user(self, client_auth, mock_open_auth, requests_mock,
                       creds_path, username, clientkey):
        # should be last call - no call to write
        mock_open_auth.assert_called_with(creds_path, 'r')
        assert requests_mock.call_count == 0

        assert client_auth.username == username
        assert client_auth.clientkey == clientkey

    # TODO: fetch entertainment groups


class TestHueStream:

    @pytest.fixture
    def group_id(self):
        return 7

    @pytest.fixture
    def client_mock(self, mocker):
        mock = mocker.MagicMock()
        type(mock).clientkey = mocker.PropertyMock(return_value='deadbeef')
        return mock

    @pytest.fixture
    def stream(self, group_id, client_mock, mocker):
        mocker.patch('mbedtls.tls.DTLSConfiguration')
        mocker.patch('mbedtls.tls.ClientContext')
        return HueStream(group_id, client_mock)

    def test_stores_group_id(self, group_id, stream):
        assert stream.group_id == group_id

    def test_start_enables_streaming(self, group_id, stream):
        stream.start()
        stream.client.set_stream_mode.assert_called_with(group_id, True)

    def test_stop_disables_streaming(self, group_id, stream):
        stream.stop()
        stream.client.set_stream_mode.assert_called_with(group_id, False)


class TestHueStreamMessage:

    @pytest.fixture
    def header(self):
        return HueStream.Message._HEADER

    @pytest.fixture
    def message(self):
        return HueStream.Message()

    def test_header_protocolname(self, header):
        assert header.startswith(b'HueStream')

    def test_header_apiversion(self, header):
        assert header[9:11] == b'\x01\x00'

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

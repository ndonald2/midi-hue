from midihue.hue import HueStream
import pytest


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

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

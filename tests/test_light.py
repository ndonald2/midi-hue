import pytest
from midihue import Light


class TestLight:

    @pytest.fixture
    def light(self):
        light = Light(7)
        light.r = 0.2
        light.g = 0.3
        light.b = 0.4
        return light

    def test_light_id(self, light):
        assert light.light_id == 7

    def test_get_set_r(self, light):
        light.r = 0.7
        assert light.r == 0.7

    def test_get_set_g(self, light):
        light.g = 0.7
        assert light.g == 0.7

    def test_get_set_b(self, light):
        light.b = 0.7
        assert light.b == 0.7

    def test_get_rgb(self, light):
        assert light.rgb() == (0.2, 0.3, 0.4)

    def test_get_rgb_int(self, light):
        assert light.rgb_int() == (13107, 19660, 26214)

import pytest
from midihue import Light


class TestLight:

    @pytest.fixture
    def light(self):
        light = Light(7)
        light.r = 0.15
        light.g = 0.3
        light.b = 0.4
        return light

    # --- RGB ---

    def test_get_rgb(self, light):
        assert light.rgb == (0.15, 0.3, 0.4)

    @pytest.mark.parametrize(
        'value,expected',
        [
            ((0.1, 0.75, 0.22), (0.1, 0.75, 0.22)),
            ((-0.1, 5, -4), (0.0, 1.0, 0.0))
        ]
    )
    def test_set_rgb(self, light, value, expected):
        light.rgb = value
        assert light.rgb == expected
        assert light.r == expected[0]
        assert light.g == expected[1]
        assert light.b == expected[2]

    def test_get_rgb_int(self, light):
        assert light.rgb_int == (9830, 19660, 26214)

    @pytest.mark.parametrize(
        'value,expected',
        [(0.7, 0.7), (-0.2, 0.0), (30, 1.0)]
    )
    class TestRGBSetters:

        def test_get_set_r(self, light, value, expected):
            light.r = value
            assert light.r == expected

        def test_get_set_g(self, light, value, expected):
            light.g = value
            assert light.g == expected

        def test_get_set_b(self, light, value, expected):
            light.b = value
            assert light.b == expected

    # --- HSV ---

    def test_get_hsv(self, light):
        assert light.hsv == (0.5666666666666668, 0.625, 0.4)

    @pytest.mark.parametrize(
        'value,expected_rgb',
        [
            ((0.5, 1.0, 1.0), (0.0, 1.0, 1.0)),
            ((-0.1, 1.2, 0.25), (0.25, 0.0, 0.0))
        ]
    )
    def test_set_hsv(self, light, value, expected_rgb):
        light.hsv = value
        assert light.rgb == expected_rgb

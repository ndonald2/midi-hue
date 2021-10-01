import pytest
from math import isclose
from midihue import Light


class TestLight:

    @pytest.fixture(params=['rgb', 'hsv'])
    def light(self, request):
        light = Light(7, colorspace=request.param)
        light.rgb = (0.15, 0.3, 0.4)
        return light

    # --- RGB ---

    def test_get_rgb(self, light):
        rgb = light.rgb
        assert isclose(rgb.r, 0.15)
        assert isclose(light.r, 0.15)
        assert isclose(rgb.g, 0.3)
        assert isclose(light.g, 0.3)
        assert isclose(rgb.b, 0.4)
        assert isclose(light.b, 0.4)

    @pytest.mark.parametrize(
        'value,expected',
        [
            ((0.1, 0.75, 0.22), (0.1, 0.75, 0.22)),
            ((-0.1, 5, -4), (0.0, 1.0, 0.0))
        ]
    )
    def test_set_rgb_get_rgb(self, light, value, expected):
        light.rgb = value
        rgb = light.rgb
        assert isclose(rgb.r, expected[0])
        assert isclose(light.r, expected[0])
        assert isclose(rgb.g, expected[1])
        assert isclose(light.g, expected[1])
        assert isclose(rgb.b, expected[2])
        assert isclose(light.b, expected[2])

    @pytest.mark.parametrize(
        'value,expected',
        [
            ((0.1, 0.75, 0.22), (0.36410256410256414, 0.86666666666666, 0.75)),
            ((-0.1, 5, -4), (1.0/3.0, 1.0, 1.0))
        ]
    )
    def test_set_rgb_get_hsv(self, light, value, expected):
        light.rgb = value
        hsv = light.hsv
        assert isclose(hsv.h, expected[0])
        assert isclose(light.h, expected[0])
        assert isclose(hsv.s, expected[1])
        assert isclose(light.s, expected[1])
        assert isclose(hsv.v, expected[2])
        assert isclose(light.v, expected[2])

    def test_get_rgb_int(self, light):
        assert light.rgb_int == (9830, 19660, 26214)

    @pytest.mark.parametrize(
        'value,expected',
        [
            (0.7, 0.7),
            (-0.2, 0.0),
            (30, 1.0)
        ]
    )
    class TestRGBSetters:

        def test_get_set_r(self, light, value, expected):
            light.r = value
            assert isclose(light.r, expected)

        def test_get_set_g(self, light, value, expected):
            light.g = value
            assert isclose(light.g, expected)

        def test_get_set_b(self, light, value, expected):
            light.b = value
            assert isclose(light.b, expected)

    # --- HSV ---

    def test_get_hsv(self, light):
        hsv = light.hsv
        assert isclose(hsv.h, 17.0/30)
        assert isclose(light.h, 17.0/30)
        assert isclose(hsv.s, 0.625)
        assert isclose(light.s, 0.625)
        assert isclose(hsv.v, 0.4)
        assert isclose(light.v, 0.4)

    @pytest.mark.parametrize(
        'value,expected',
        [
            ((0.1, 0.75, 0.22), (0.1, 0.75, 0.22)),
            ((0.2, 5, 0.3), (0.2, 1.0, 0.3))
        ]
    )
    def test_set_hsv_get_hsv(self, light, value, expected):
        light.hsv = value
        hsv = light.hsv
        assert isclose(hsv.h, expected[0])
        assert isclose(light.h, expected[0])
        assert isclose(hsv.s, expected[1])
        assert isclose(light.s, expected[1])
        assert isclose(hsv.v, expected[2])
        assert isclose(light.v, expected[2])

    @pytest.mark.parametrize(
        'value,expected',
        [
            ((0.5, 1.0, 1.0), (0.0, 1.0, 1.0)),
            ((-0.1, 1.2, 0.25), (0.25, 0.0, 0.0))
        ]
    )
    def test_set_hsv_get_rgb(self, light, value, expected):
        light.hsv = value
        rgb = light.rgb
        assert isclose(rgb.r, expected[0])
        assert isclose(light.r, expected[0])
        assert isclose(rgb.g, expected[1])
        assert isclose(light.g, expected[1])
        assert isclose(rgb.b, expected[2])
        assert isclose(light.b, expected[2])

    @pytest.mark.parametrize(
        'value,expected',
        [
            (0.7, 0.7),
            (-0.2, 0.0),
            (30, 1.0)
        ]
    )
    class TestHSVSetters:

        def test_get_set_h(self, light, value, expected):
            light.h = value
            if light._colorspace == 'rgb' and expected == 1.0:
                assert light.h == 0.0 or light.h == 1.0
            else:
                assert isclose(light.h, expected)

        def test_get_set_s(self, light, value, expected):
            light.s = value
            assert isclose(light.s, expected)

        def test_get_set_v(self, light, value, expected):
            light.v = value
            assert isclose(light.v, expected)

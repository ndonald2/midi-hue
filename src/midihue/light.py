from collections import namedtuple
from colorsys import rgb_to_hsv, hsv_to_rgb


def _clampunit(i):
    return max(0., min(1.0, i))


RGB = namedtuple('RGB', ['r', 'g', 'b'])
HSV = namedtuple('HSV', ['h', 's', 'v'])


class Light:

    # Colorspace must be 'hsv' or 'rgb'. Either option supports conversion
    # between the two spaces but the value passed here determines how color
    # data is stored natively.
    def __init__(self, light_id, colorspace='hsv', bits_per_channel=16):
        assert colorspace in ('rgb', 'hsv')
        self.light_id = light_id
        self._colorspace = colorspace
        self._bits_per_channel = bits_per_channel
        if colorspace == 'hsv':
            self._hsv = HSV(0, 0, 0)
        else:
            self._rgb = RGB(0, 0, 0)

    def __getattr__(self, name):
        if name in ('h', 's', 'v'):
            return getattr(self.hsv, name)
        elif name in ('r', 'g', 'b'):
            return getattr(self.rgb, name)
        else:
            raise AttributeError(f'Attribute {name} not found')

    def __setattr__(self, name, value):
        if name in ('r', 'g', 'b'):
            rgb = list(self.rgb)
            rgb['rgb'.index(name)] = _clampunit(value)
            self.rgb = rgb
        elif name in ('h', 's', 'v'):
            hsv = list(self.hsv)
            hsv['hsv'.index(name)] = _clampunit(value)
            self.hsv = hsv
        else:
            object.__setattr__(self, name, value)

    @property
    def rgb(self):
        if self._colorspace == 'hsv':
            return RGB(*hsv_to_rgb(*self._hsv))
        else:
            return self._rgb

    @rgb.setter
    def rgb(self, value):
        assert len(value) == 3
        rgb = RGB(
            _clampunit(value[0]),
            _clampunit(value[1]),
            _clampunit(value[2])
        )
        if self._colorspace == 'hsv':
            self._hsv = HSV(*rgb_to_hsv(*rgb))
        else:
            self._rgb = rgb

    @property
    def rgb_int(self):
        max_int = (1 << self._bits_per_channel) - 1
        rgb = self.rgb
        return (
            int(rgb.r * max_int),
            int(rgb.g * max_int),
            int(rgb.b * max_int)
        )

    @property
    def hsv(self):
        if self._colorspace == 'hsv':
            return self._hsv
        else:
            return HSV(*rgb_to_hsv(*self._rgb))

    @hsv.setter
    def hsv(self, value):
        assert len(value) == 3
        hsv = HSV(
            _clampunit(value[0]),
            _clampunit(value[1]),
            _clampunit(value[2])
        )
        if self._colorspace == 'hsv':
            self._hsv = hsv
        else:
            self._rgb = RGB(*hsv_to_rgb(*hsv))

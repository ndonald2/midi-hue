from collections import namedtuple
from colorsys import rgb_to_hsv, hsv_to_rgb


def _clampunit(i):
    return max(0., min(1.0, i))


RGB = namedtuple('RGB', ['r', 'g', 'b'])


HSV = namedtuple('HSV', ['h', 's', 'v'])


class Light:

    def __init__(self, light_id, bits_per_channel=16):
        self.light_id = light_id
        self._r = 0
        self._g = 0
        self._b = 0
        self._bits_per_channel = bits_per_channel

    def __getattr__(self, name):
        if name in ('r', 'g', 'b'):
            return getattr(self, f'_{name}')
        else:
            raise AttributeError(f'Attribute {name} not found')

    def __setattr__(self, name, value):
        if name in ('r', 'g', 'b'):
            # Clamp to 0.0 - 1.0 float range
            setattr(self, f'_{name}', _clampunit(value))
        else:
            object.__setattr__(self, name, value)

    @property
    def rgb(self):
        return RGB(self.r, self.g, self.b)

    @rgb.setter
    def rgb(self, value):
        assert len(value) == 3
        self.r = value[0]
        self.g = value[1]
        self.b = value[2]

    @property
    def rgb_int(self):
        max_int = (1 << self._bits_per_channel) - 1
        return (
            int(self.r * max_int),
            int(self.g * max_int),
            int(self.b * max_int)
        )

    @property
    def h(self):
        return self.hsv.h

    @h.setter
    def h(self, value):
        hsv = self.hsv
        hsv.h = _clampunit(value)
        self.rgb = hsv_to_rgb(*hsv)

    @property
    def s(self):
        return self.hsv.s

    @s.setter
    def s(self, value):
        hsv = self.hsv
        hsv.s = _clampunit(value)
        self.rgb = hsv_to_rgb(*hsv)

    @property
    def v(self):
        return self.hsv.v

    @v.setter
    def v(self, value):
        hsv = self.hsv
        hsv.v = _clampunit(value)
        self.rgb = hsv_to_rgb(*hsv)

    @property
    def hsv(self):
        return HSV(*rgb_to_hsv(*self.rgb))

    @hsv.setter
    def hsv(self, value):
        assert len(value) == 3
        self.rgb = rgb_to_hsv(
            _clampunit(value[0]),
            _clampunit(value[1]),
            _clampunit(value[2])
        )

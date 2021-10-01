from colorsys import rgb_to_hsv, hsv_to_rgb


def _clampunit(i):
    return max(0., min(1.0, i))


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
            setattr(self, f'_{name}', _clampunit(value))
        else:
            object.__setattr__(self, name, value)

    def rgb(self):
        return (self.r, self.g, self.b)

    def rgb_int(self):
        max_int = (1 << self._bits_per_channel) - 1
        return (
            int(self.r * max_int),
            int(self.g * max_int),
            int(self.b * max_int)
        )

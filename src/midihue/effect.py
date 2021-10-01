
class _BaseEffect:

    def __init__(self, light):
        self.light = light
        self.msg_type = None
        self.msg_channel = None

    def process(self, messages):
        raise NotImplementedError


class DirectMapping(_BaseEffect):

    TARGET_ATTR_MAP = {
        'red': 'r',
        'green': 'g',
        'blue': 'b',
        'hue': 'h',
        'saturation': 's',
        'brightness': 'v',
        'value': 'v'
    }

    def __init__(self, light, target='brightness', **kwargs):
        _BaseEffect.__init__(self, light)
        self.msg_type = kwargs.get('messagetype') or 'control_change'
        self.msg_channel = kwargs.get('channel')
        self.target = self.TARGET_ATTR_MAP.get(target) or target

    def process(self, messages):
        # For this effect we only care about the most recent
        # message that matches our criteria.
        filtered = list(filter(self._filter, messages))
        if not filtered:
            return
        msg = filtered[-1]
        setattr(self.light, self.target, msg.value / 127.0)

    def _filter(self, message):
        try:
            if message.type != self.msg_type:
                return False
            if self.msg_channel is not None and \
                    message.channel != self.msg_channel:
                return False
            return True
        except AttributeError as error:
            print(error)
            return False

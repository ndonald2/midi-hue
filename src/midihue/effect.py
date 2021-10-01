
class _BaseEffect:

    TARGET_ATTR_MAP = {
        'red': 'r',
        'green': 'g',
        'blue': 'b',
        'hue': 'h',
        'saturation': 's',
        'brightness': 'v',
        'value': 'v'
    }

    def __init__(self, light, target, **kwargs):
        self.light = light
        self._target = self.TARGET_ATTR_MAP.get(target) or target
        self.__dict__.update(kwargs)

    def process(self, messages):
        raise NotImplementedError

    def _should_handle_message(self, message):
        try:
            if message.type != self.messagetype:
                return False

            if self.channel is not None and \
                    message.channel != self.channel:
                return False

            if message.type == 'control_change':
                if self.control is not None and \
                        message.control != self.control:
                    return False

            if message.type in ('note_on', 'note_off'):
                if self.note is not None and \
                        message.note != self.note:
                    return False

            return True
        except AttributeError as error:
            print(error)
            return False

    def _get_norm_value(self, message):
        if message.type == 'control_change':
            return message.value / 127.0
        elif message.type == 'note_on':
            return 1.0
        elif message.type == 'note_off':
            return 0.0


class Direct(_BaseEffect):

    def __init__(self, light, target, scalefactor=1.0, **kwargs):
        super(Direct, self).__init__(light, target, **kwargs)
        self.scalefactor = scalefactor

    def process(self, messages):
        # For this effect we only care about the most recent
        # message that matches the criteria.
        filtered = list(filter(self._should_handle_message, messages))
        if not filtered:
            return
        msg = filtered[-1]
        setattr(self.light,
                self._target,
                self._get_norm_value(msg) * self.scalefactor)


class _MessageFilters:

    class _Condition:

        # Indicates filter param names that should always
        # return as a match if absent. i.e. if there is no
        # filter value for 'channel' any channel value is a match
        WILCARD_NAMES = [
            'channel',
            'note'
        ]

        def __init__(self, name, value):
            self.name = name
            self.value = value

        def __eq__(self, obj):
            if self.value is None and self.name in self.WILCARD_NAMES:
                return True
            else:
                return obj == self.value

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        value = self.__dict__.get(name)
        return self._Condition(name, value)


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
        self._filters = _MessageFilters(**kwargs)

    def process(self, messages):
        raise NotImplementedError

    def _should_handle_message(self, message):
        try:
            if message.type != self._filters.messagetype:
                return False

            if message.channel != self._filters.channel:
                return False

            if message.type == 'control_change':
                if message.control != self._filters.control:
                    return False

            if message.type in ('note_on', 'note_off'):
                if message.note != self._filters.note:
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
        value = self._get_norm_value(msg)
        if value is not None:
            setattr(self.light, self._target, value * self.scalefactor)

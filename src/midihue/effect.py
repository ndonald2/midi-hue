
# Effects are meant to processed at a relatively slow rate ~100Hz
# Therefore they accept a list of MIDI messages which have arrived
# since the last loop iteration. Each effect decides how to handle
# the messages - maybe they are all important, maybe only the most
# recent match.

class _BaseEffect:

    supported_message_types = []
    discard_redundant_messages = False

    def __init__(self, light):
        self.light = light

    def process(self, messages):
        filtered = list(filter(self.should_handle_message, messages))
        if not filtered:
            return
        if self.discard_redundant_messages:
            self.handle_message(filtered[-1])
        else:
            for message in filtered:
                self.handle_message(message)

    def should_handle_message(self, message):
        return message.type in self.supported_message_types

    def handle_message(self, message):
        raise NotImplementedError


class _ClockEffect(_BaseEffect):

    PPQN = 24

    supported_message_types = [
        'clock',
        'start',
        'stop',
        'continue'
    ]


# Effect mapped from a controller or note on/off message
# (TODO: pitch wheel, other common variable messages)
class _ControlEffect(_BaseEffect):

    supported_message_types = [
        'control_change',
        'note_on',
        'note_off'
    ]

    class _MessageFilters:

        PLURAL_MAPPINGS = {
            'channels': 'channel',
            'controls': 'control',
            'notes': 'note'
        }

        class _Condition:

            # Indicates filter param names that should always
            # return as a match if absent. i.e. if there is no
            # filter value for 'channel' any channel value is a match
            WILCARD_NAMES = [
                'channel',
                'control',
                'note'
            ]

            def __init__(self, name, value):
                self.name = name
                self.value = value

            def matches(self, obj):
                if self.value is None and self.name in self.WILCARD_NAMES:
                    return True
                try:
                    return obj in self.value
                except TypeError:
                    return obj == self.value

        def __init__(self, **kwargs):
            self._raw = kwargs

        def __getattr__(self, name):
            alt_key = self.PLURAL_MAPPINGS.get(name)
            value = self._raw.get(name) or self._raw.get(alt_key)
            return self._Condition(name, value)

    def __init__(self, light, **kwargs):
        super(_ControlEffect, self).__init__(light)
        self._filters = self._MessageFilters(**kwargs)

    def should_handle_message(self, message):
        if not super(_ControlEffect, self).should_handle_message(message):
            return False

        if not self._filters.messagetype.matches(message.type):
            return False

        if not self._filters.channel.matches(message.channel):
            return False

        if message.type == 'control_change':
            if not self._filters.controls.matches(message.control):
                return False
        elif message.type in ('note_on', 'note_off'):
            if not self._filters.notes.matches(message.note):
                return False

        return True


class _TriggeredEffect(_ControlEffect):
    pass


# Direct control over a single light attribute
class DirectControlEffect(_ControlEffect):

    TARGET_ATTR_MAP = {
        'red': 'r',
        'green': 'g',
        'blue': 'b',
        'hue': 'h',
        'saturation': 's',
        'brightness': 'v',
        'value': 'v'
    }

    discard_redundant_messages = True

    def __init__(self, light, target, scalefactor=1.0, **kwargs):
        super(DirectControlEffect, self).__init__(light, **kwargs)
        self._target = self.TARGET_ATTR_MAP.get(target) or target
        self.scalefactor = scalefactor

    def handle_message(self, message):
        value = self._get_norm_value(message)
        if value is not None:
            setattr(self.light, self._target, value * self.scalefactor)

    def _get_norm_value(self, message):
        if message.type == 'control_change':
            return message.value / 127.0
        elif message.type == 'note_on':
            return 1.0
        elif message.type == 'note_off':
            return 0.0

import time
import mido
from .hue import HueClient, HueStream


class MidiHueCLI:

    # Temporarily hardcoded
    GROUP_ID = 2

    def __init__(self):
        pass

    def run(self):
        v1 = 0
        v2 = 0
        v3 = 0

        client = HueClient()
        stream = HueStream(self.GROUP_ID, client)
        stream.start()
        inport = mido.open_input('IAC Driver IAC Bus 1')

        def handle_midi(msg):
            global v1, v2, v3
            if msg.type == 'control_change':
                if msg.control == 77:
                    v1 = msg.value << 9
                elif msg.control == 78:
                    v2 = msg.value << 9
                elif msg.control == 79:
                    v3 = msg.value << 9

        while True:
            for msg in inport.iter_pending():
                handle_midi(msg)
            streammsg = HueStream.Message()
            streammsg.add(light_id=3, rgb=[0, v1, 0])
            streammsg.add(light_id=4, rgb=[0, 0, v2])
            streammsg.add(light_id=10, rgb=[v3, 0, 0])
            stream.send(streammsg)
            time.sleep(0.01)

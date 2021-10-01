import time
import click
import mido
from .light import Light
from .hue import HueClient, HueStream, DEFAULT_CREDENTIALS_PATH


@click.command()
@click.option('--credentials-path',
              default=DEFAULT_CREDENTIALS_PATH,
              show_default=True,
              type=click.Path(exists=False),
              help="Path to the file where Hue user credentials "
                   "are loaded/stored.")
@click.option('--group-id',
              default=None,
              type=int,
              help="The ID of the light group you want to control "
                   "on your Hue bridge. Must be an Entertainment group. ")
@click.option('--input-name',
              default=None,
              type=str,
              help="The name of the MIDI input from which to "
                   "observe messages.")
def main(group_id, input_name, credentials_path):
    """Programmable MIDI control over Philips Hue lights"""

    client = HueClient(credentials_path=credentials_path)

    if group_id is None:
        groups = client.get_entertainment_groups()
        if not groups:
            print("No Entertainment groups found on your Hue bridge. "
                  "Please use the Hue app to create one and try again.")
            exit(0)

        groups_formatted = '\n'.join([f'{gid}. {desc}' for gid, desc
                                     in groups])
        group_id = click.prompt('\nEnter ID of light group to control\n\n'
                                f'{groups_formatted}\n\nGroup ID',
                                type=int)

    if input_name is None:
        # quick and dirty dedupe until mido fix is released to pypi
        # https://github.com/mido/mido/pull/321
        inputs = list(dict.fromkeys(mido.get_input_names()))
        inputs_formatted = '\n'.join([f'{idx}. {name}' for idx, name
                                      in enumerate(inputs)])
        input_index = click.prompt(f'\nChoose a MIDI input\n\n'
                                   f'{inputs_formatted}\n\nInput', type=int)
        input_name = inputs[input_index]

    stream = HueStream(group_id, client)
    inport = mido.open_input(input_name)

    stream.start()
    _loop(inport, stream)


# Temporary hard coded mapping
# Next big TODO: make this configurable
def _loop(inport, stream):
    l1 = Light(3)
    l2 = Light(4)
    l3 = Light(10)

    for light in (l1, l2, l3):
        light.hsv = (0.0, 1.0, 1.0)

    while True:
        for msg in inport.iter_pending():
            if msg.type == 'control_change':
                if msg.control == 77:
                    l1.h = msg.value / 127.0
                elif msg.control == 78:
                    l1.s = msg.value / 127.0
                elif msg.control == 79:
                    l1.v = msg.value / 127.0

        streammsg = HueStream.Message()
        for light in (l1, l2, l3):
            streammsg.add(light.light_id, light.rgb_int)

        stream.send(streammsg)
        time.sleep(0.01)

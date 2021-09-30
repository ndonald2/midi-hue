import time
import click
import mido
from .hue import HueClient, HueStream, DEFAULT_CREDENTIALS_PATH


@click.command()
@click.option('--credentials-path',
              default=DEFAULT_CREDENTIALS_PATH,
              show_default=True,
              type=click.Path(exists=False),
              help="Path to the file where Hue user credentials "
                   "are loaded/stored.")
@click.option('--light-group',
              default=None,
              type=int,
              help="The ID of the light group you want to control "
                   "on your Hue bridge. Must be an Entertainment group. ")
@click.option('--input-name',
              default=None,
              type=str,
              help="The name of the MIDI input from which to "
                   "observe messages.")
def main(light_group, input_name, credentials_path):
    """Programmable MIDI control over Philips Hue lights"""

    client = HueClient(credentials_path=credentials_path)

    if light_group is None:
        groups = client.get_entertainment_groups()
        if not groups:
            print("No Entertainment groups found on your Hue bridge. "
                  "Please use the Hue app to create one and try again.")
            exit(0)

        groups_formatted = '\n'.join([f'{gid}. {desc}' for gid, desc
                                     in groups])
        light_group = click.prompt('\nEnter ID of light group to control\n\n'
                                   f'{groups_formatted}\n\nGroup ID',
                                   type=int)

    if input_name is None:
        inputs = mido.get_input_names()
        inputs_formatted = '\n'.join([f'{idx}. {name}' for idx, name
                                      in enumerate(inputs)])
        input_index = click.prompt(f'\nChoose a MIDI input\n\n'
                                   f'{inputs_formatted}\n\nInput', type=int)
        input_name = inputs[input_index]

    stream = HueStream(light_group, client)
    inport = mido.open_input(input_name)

    stream.start()
    _loop(inport, stream)


# Temporary hard coded mapping
# Next big TODO: make this configurable
def _loop(inport, stream):
    v1 = 0
    v2 = 0
    v3 = 0

    while True:
        for msg in inport.iter_pending():
            if msg.type == 'control_change':
                if msg.control == 77:
                    v1 = msg.value << 9
                elif msg.control == 78:
                    v2 = msg.value << 9
                elif msg.control == 79:
                    v3 = msg.value << 9

        streammsg = HueStream.Message()
        streammsg.add(light_id=3, rgb=(0, v1, 0))
        streammsg.add(light_id=4, rgb=(0, 0, v2))
        streammsg.add(light_id=10, rgb=(v3, 0, 0))
        stream.send(streammsg)
        time.sleep(0.01)

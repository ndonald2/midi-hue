import time
import click
import mido
from . import effect
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
    light = Light(3)
    mappings = [
        effect.Direct(light,
                      'saturation',
                      channel=8,
                      messagetype='control_change',
                      control=77),
        effect.Direct(light,
                      'brightness',
                      channel=8,
                      messagetype='control_change',
                      control=78),
        effect.Direct(light,
                      'hue',
                      scalefactor=0.2,
                      channel=8,
                      messagetype='note_on',
                      note=73),
        effect.Direct(light,
                      'hue',
                      channel=8,
                      messagetype='note_off',
                      note=73)
    ]

    while True:
        msgs = list(inport.iter_pending())
        for mpg in mappings:
            mpg.process(msgs)

        streammsg = HueStream.Message()
        streammsg.add(light.light_id, light.rgb_int)

        stream.send(streammsg)
        time.sleep(0.01)

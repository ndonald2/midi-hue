midi-hue
========

Programmable control of Philips Hue lights using MIDI

### ⚠️  This package is a WIP and should not be considered stable

## Requirements

* Python 3.6+
* Supports macOS. _Should_ work on Linux, but not tested yet. Windows TBD. 
* `mbedtls 2.x` package must be installed and linked on your system
    * macOS: `brew install mbedtls@2`
    * debian/ubuntu: `sudo apt-get install libmbedtls-dev`
    * windows/other: good luck!

## Installation

This package is not yet registered with PyPI so you will need to install it from source. 
For development purposes, clone the repo and run `bin/setup-dev`.

You can also try installing with `pip` but **currently this is not a good idea** since
the package isn't generally useful without code customizations for your own setup.

```
pip install pip install https://github.com/ndonald2/midi-hue.git
```

## Usage

The package provides a CLI entry point: `midi-hue`

Run `midi-hue --help` to print usage details.

Bridge discovery is automatic and chooses the first bridge in your local network if you have
more than one. Upon running the first time you should be prompted to press the physical button
on your Hue bridge and run again. This is necessary for the auth process to verify you have
physical access to the bridge. After that, the auth credentials will be persisted to `~/.midihue`
by default, but this can be overridden with a CLI flag (TODO: support environment variables).

You will need at least one Entertainment Area setup on your Hue network, which can be done with
the Hue mobile app(s). You will also need at least one MIDI input device on your computer.

__⚠️  Note that at this point in time the MIDI->Hue mappings are using hard coded CC values and
light IDs. Configurable mappings are coming soon but in the meantime you will need to change
the code in `src/cli.py`__

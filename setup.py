from setuptools import setup, find_packages

setup(
    name='MIDIHue',
    version='0.0.1',
    author='Nick Donaldson',
    author_email='ndonald2@gmail.com',
    description='Programmable control of Philips Hue lights using MIDI',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=[
        'python-mbedtls',
        'requests'
    ],
    extras_require={
        'dev': ['flake8', 'autopep8']
    }
)

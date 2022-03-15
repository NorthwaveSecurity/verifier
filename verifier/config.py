import configparser
import os

config_locations = [
    os.path.join(os.path.dirname(__file__), '../config.ini'),
    os.path.expanduser('~/.config/verifier.ini'),
]
config = configparser.ConfigParser()
for config_location in config_locations:
    config.read(config_location)

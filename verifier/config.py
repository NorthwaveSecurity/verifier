import configparser
import os

user_config = os.path.expanduser('~/.config/verifier.ini')

config_locations = [
    os.path.join(os.path.dirname(__file__), '../config.ini'),
    user_config,
]
config = configparser.ConfigParser()
for config_location in config_locations:
    config.read(config_location)

def configure():
    sections = []
    for i, x in enumerate(config.keys()):
        sections.append(x)
        print(f"{i}: {x}")
    section = int(input("Which section would you like to edit [0-{}] ".format(len(config.keys()))))
    section_key = sections[section]
    print("Editing section: {}".format(section_key))
    keys = []
    for i, x in enumerate(config.options(section_key)):
        keys.append(x)
        print(f"{i}: {x}")
    key_num = int(input("Which key would you like to edit [0-{}] ".format(len(keys))))
    key = keys[key_num]
    print("Editing {}: {}".format(key, config[section_key][key]))
    value = input("New value: ")
    config.set(section_key, key, value)
    with open(user_config, 'w') as f:
        config.write(f)

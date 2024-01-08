import configparser
import os
import sys

user_config = os.path.expanduser('~/.config/verifier.ini')

config_locations = [
    os.path.join(os.path.dirname(__file__), '../config.ini'),
    user_config,
]
if 'VERIFIER_CONFIG' in os.environ:
    config_locations.append(os.environ['VERIFIER_CONFIG'])

config = configparser.ConfigParser()
config.default_section = "fallback"
for config_location in config_locations:
    config.read(config_location)


def configure():
    print("Current configuration: ")
    config.write(sys.stdout)
    print()

    sections = [key for key in config.keys() if key != config.default_section]
    for i, x in enumerate(sections):
        print(f"{i}: {x}")
    section = int(input("Which section would you like to edit [0-{}] ".format(len(sections)-1)))
    section_key = sections[section]
    print("Editing section: {}".format(section_key))
    keys = [key for key in config.options(section_key)]
    for i, x in enumerate(keys):
        print(f"{i}: {x}")
    key_num = int(input("Which key would you like to edit [0-{}] ".format(len(keys)-1)))
    key = keys[key_num]
    print("Editing {}: {}".format(key, config[section_key][key]))
    value = input("New value: ")
    config.set(section_key, key, value)
    with open(user_config, 'w') as f:
        config.write(f)

if __name__ == "__main__":
    from pathlib import Path
    config.write(sys.stdout)
    print("============================================================")
    print("Loaded config files:")
    for l in config_locations:
        exists = "exists" if Path(l).exists() else "does not exist"
        print(f"{l}: {exists}")

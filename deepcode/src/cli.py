import sys
import argparse

# TODO: temporary here for tests
cli_avaliable_args = [
    {
        "command": "--login",
        "shortcut": "-lgi",
        "help": "help string",
        "action": "store_true"
    },
    {
        "command": "--logout",
        "shortcut": "-lgo",
        "help": "help string",
        "action": "store_true"
    },
    {
        "command": "--analyze",
        "shortcut": "-a",
        "help": "help string",
        "action": "store_true"
    },
    {
        "command": "--config",
        "shortcut": "-c",
        "help": "help string",
        "action": "store_true"
    }
]


def cli_entry_point():
    parser = argparse.ArgumentParser(description="DeepCode CLI arguments")
    for arg in cli_avaliable_args:
        command, shortcut, help, action = arg.values()
        parser.add_argument(shortcut, command, help=help, action=action)
    args = parser.parse_args()
    # TODO
    if len(sys.argv) == 1:
        parser.print_help()
        return
    print(args)

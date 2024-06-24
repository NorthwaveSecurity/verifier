import argparse
from ..evidence_savers import evidence_savers

class Runner:
    name = "TODO"
    help = "TODO"
    parser = None
    def __init__(self, subparsers):
        self.parser = subparsers.add_parser(self.name, help=self.help)
        self.parser.set_defaults(func=self.caller)
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument("-s", "--save", nargs='?', default=argparse.SUPPRESS, choices=evidence_savers.keys(), help="Save the issue using the default issue saver")

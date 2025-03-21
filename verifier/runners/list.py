from .base import Runner as Base
from ..verifier import show_issue_list

class ListRunner(Base):
    name = "list"
    help = "List all supported issues"

    def add_arguments(self):
        pass

    def caller(self, args, extra_args):
        show_issue_list(args, extra_args)
        
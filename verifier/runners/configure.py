from .base import Runner as Base
from ..config import configure

class ConfigureRunner(Base):
    name = "config"
    help = "Configure verifier"

    def add_arguments(self):
        pass

    def caller(self, args, extra_args):
        configure()
        
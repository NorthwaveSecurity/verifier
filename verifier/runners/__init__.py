from .configure import Runner as ConfigureRunner
from .importer import Runner as ImportRunner
from .verify import Runner as VerifyRunner
from .list import Runner as ListRunner

runners = [VerifyRunner, ImportRunner, ConfigureRunner, ListRunner]

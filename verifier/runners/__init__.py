from .configure import Runner as ConfigureRunner
from .importer import Runner as ImportRunner
from .verify import Runner as VerifyRunner
from .list import Runner as ListRunner
from .nessus import Runner as NessusRunner

runners = [VerifyRunner, ImportRunner, ConfigureRunner, ListRunner, NessusRunner]

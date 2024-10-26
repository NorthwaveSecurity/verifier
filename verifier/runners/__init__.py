from .configure import ConfigureRunner
from .importer import ImportRunner
from .verify import VerifyRunner
from .list import ListRunner
from .nessus import NessusRunner
from .create import CreateRunner

runners = [VerifyRunner, ImportRunner, ConfigureRunner, ListRunner, NessusRunner, CreateRunner]

from .base import Runner as Base
from ..verifier import get_evidence_saver, import_evidences, process_evidence
from ..config import config

class Runner(Base):
    name = "import"
    help = "Import results from file"

    def add_arguments(self):
        super().add_arguments()
        self.parser.add_argument("import_file", help="File to import")

    def caller(self, args, extra_args):
        if 'save' in args:
            save = args.save or config['DEFAULT'].get('evidence_saver')
        else:
            save = None
        evidence_saver, _ = get_evidence_saver(save, extra_args)
        evidences = import_evidences(args.import_file)
        for evidence in evidences:
            process_evidence(evidence, evidence_saver=evidence_saver)
        
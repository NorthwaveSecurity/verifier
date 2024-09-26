import logging
from .verify import Runner as Base
from ..verifier import get_evidence_saver
from ..issues.base import Evidence, issues
from ..content_reader import read_content
from ..verifier import get_issue_ids, get_proxy, verify, export_evidences
from ..config import config

class Runner(Base):
    name = "nessus"
    help = "Process nessus export"

    def add_arguments(self):
        super().add_verify_arguments()
        self.parser.add_argument("-i", "--input-file", required=True, help="Nessus input file")

    def caller(self, args, extra_args):
        if args.proxy:
            logging.info(f"Using proxy server: {args.proxy}")
        evidences = []
        if 'save' in args:
            save = args.save or config['DEFAULT'].get('evidence_saver')
        else:
            save = None
        # PARSE nessus file
        for result in parse_nessus(args.input_file):
            try:
                for evidence in verify(
                        result.issue,
                        result.target,
                        save=save,
                        label=result.label,
                        lang=args.lang,
                        proxy=args.proxy,
                        content=None,
                        extra_args=extra_args):
                    evidences.append(evidence)
            finally:
                if evidences and args.export_file:
                    export_evidences(evidences, args.export_file)

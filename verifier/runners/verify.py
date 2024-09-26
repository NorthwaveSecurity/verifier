import logging
from .base import Runner as Base
from ..content_reader import read_content
from ..verifier import get_issue_ids, get_proxy, verify, export_evidences
from ..config import config

class Runner(Base):
    name = "verify"
    help = "Generate evidence for standard issues"

    def add_arguments(self):
        super().add_arguments()
        self.parser.add_argument("-t", "--target", required=True, nargs='*', help="Targets")
        self.parser.add_argument("-i", "--issue", required=True, choices=get_issue_ids(), nargs='*', help="Issue id to verify, use 'verifier list' to see all options, or set to 'all'", metavar='ISSUE')
        self.parser.add_argument("-c", "--content", help="File with content for the evidences, e.g. request, response, in the format described in the README")
        self.parser.add_argument("-L", "--label", help="Different label for the location in the issue")
        self.add_verify_arguments()

    def add_verify_arguments(self):
        self.parser.add_argument("-x", "--export-file", help="Export results to file for later import")
        self.parser.add_argument("-l", "--lang", choices=["en", "nl"], default="en", help="Reporting language")
        self.parser.add_argument("--proxy", nargs='?', help="Use the given proxy server, insert anything to use proxychains", default=get_proxy())

    def caller(self, args, extra_args):
        if args.proxy:
            logging.info(f"Using proxy server: {args.proxy}")
        if args.content:
            content = read_content(args.content)
        else:
            content = None
        evidences = []
        if 'save' in args:
            save = args.save or config['DEFAULT'].get('evidence_saver')
        else:
            save = None
        try:
            for evidence in verify(
                    args.issue,
                    args.target,
                    save=save,
                    label=args.label,
                    lang=args.lang,
                    proxy=args.proxy,
                    content=content,
                    extra_args=extra_args):
                evidences.append(evidence)
        finally:
            if evidences and args.export_file:
                export_evidences(evidences, args.export_file)

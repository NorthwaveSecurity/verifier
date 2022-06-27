class EvidenceSaver:
    def save_evidence(self, evidence):
        raise NotImplementedError()

    def parse_args(self, args):
        """ Parse arguments and return extra_args"""
        return args

evidence_savers = {}

def add_evidence_saver(key, issue_saver):
    evidence_savers[key] = issue_saver

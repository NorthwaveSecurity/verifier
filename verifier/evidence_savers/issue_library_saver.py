from .evidence_saver import add_evidence_saver, EvidenceSaver as Base
from ..issues import get_issue
from os.path import join
from ..config import config
from reporter import create_standard_issue, create_evidence

class EvidenceSaver(Base):
    def save_evidence(self, evidence):
        issue = get_issue(evidence.id, lang=evidence.lang)
        if issue.standard_issue_path:
            dirname = create_standard_issue(issue.standard_issue_path, output_file=None, do_create_evidence=False)
            create_evidence(evidence.host, output_dir=dirname, description=evidence.output)
        else:
            create_evidence(evidence.host, description=evidence.output)


add_evidence_saver("issue-library", EvidenceSaver())

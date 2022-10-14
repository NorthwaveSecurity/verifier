from .evidence_saver import add_evidence_saver, EvidenceSaver as Base
from ..issues import get_issue
from os.path import join
from ..config import config

class EvidenceSaver(Base):
    def save_evidence(self, evidence):
        from reporter import Template, config as reporter_config
        template = Template(reporter_config.get('template'), evidence.lang)
        issue = get_issue(evidence.id, lang=evidence.lang)
        if issue.standard_issue_path:
            dirname = template.report_manager.create_standard_issue(issue.standard_issue_path, output_file=None, do_create_evidence=False)
            template.report_manager.create_evidence(evidence.label or evidence.host, output_dir=dirname, description=evidence.output)
        else:
            template.report_manager.create_evidence(evidence.label or evidence.host, description=evidence.output)


add_evidence_saver("issue-library", EvidenceSaver)

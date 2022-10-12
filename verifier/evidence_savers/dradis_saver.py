import argparse
from .evidence_saver import add_evidence_saver, EvidenceSaver as Base
from ..issues import get_issue
from ..config import config
import logging
from argparse import ArgumentParser


class EvidenceSaver(Base):
    def __init__(self):
        api_token = config['DEFAULT']['api_token']
        url = config['DEFAULT']['url']
        from dradis import Dradis
        self.dradis = Dradis(api_token, url)

    def save_evidence(self, evidence):
        issue = get_issue(evidence.id, lang=evidence.lang)
        output = "#[Description]#\n" + evidence.output
        standard_issue = self.dradis.get_standard_issue(issue.standard_issue_id)
        issue =self. dradis.get_issue_by_title(standard_issue['title'], self.args.dradis_project)
        if not issue:
            issue = self.dradis.create_issue(self.args.dradis_project, standard_issue['content'])
        node = self. dradis.get_or_create_node(self.args.dradis_project, evidence.label or evidence.host)
        self.dradis.create_evidence(self.args.dradis_project, node['id'], issue['id'], output)
        logging.info("Issue successfully created in dradis")

    def parse_args(self, args):
        parser = ArgumentParser("Dradis Saver")
        parser.add_argument("-p", "--dradis-project", required=True, help="Dradis project to create issue for")
        self.args, extra_args = parser.parse_known_args(args)
        return extra_args
    

add_evidence_saver("dradis", EvidenceSaver)


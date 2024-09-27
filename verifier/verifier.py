#!/usr/bin/env python
from dataclasses import asdict
import json
import sys
import os

from .issues import issues, expansions, get_issue
from .issues.base import Evidence, IssueDecoder, IssueEncoder
from .util import IssueDoesNotExist
from .evidence_savers import evidence_savers

# Keep track of whether an evidence has already been printed, so dividers can be included appropriately
printed_evidence = False

def print_output(output_str, issue_id=None):
    # Don't print all output in testcases
    if os.environ.get("VERIFIER_TEST", False):
        return
    global printed_evidence
    if printed_evidence:
        print('=========================', file=sys.stderr)
    else:
        printed_evidence = True
    if issue_id:
        print(issue_id, file=sys.stderr)
        print('-------------------------', file=sys.stderr)
    print(output_str)


def get_evidence_host(id, host, lang="en", content=None, extra_args=None, label=None, **kwargs):
    issue = get_issue(id, lang=lang, content=content, extra_args=extra_args, **kwargs)
    if isinstance(host, dict):
        evidences = issue.verify(**host)
        host = host['host']
    else:
        evidences = issue.verify(host)
    for evidence in evidences:
        evidence.issue = issue
        evidence.issue_id = id
        evidence.host = host
        evidence.label = label
        evidence.lang = lang
        yield evidence


def process_evidence(evidence: Evidence, evidence_saver=None):
    print_output(evidence.output, evidence.issue_id)
    if evidence_saver:
        evidence_saver.save_evidence(evidence)


def get_evidence_saver(save, extra_args=None):
    if save is not None:
        evidence_saver = evidence_savers.get(save)()
        extra_args = evidence_saver.parse_args(extra_args)
    else:
        evidence_saver = None
    return evidence_saver, extra_args


def verify_host(id, host, save=None, label=None, lang="en", export_file=None, content=None, extra_args=None, **kwargs):
    evidence_saver, extra_args = get_evidence_saver(save, extra_args=extra_args)
    try:
        evidences = get_evidence_host(id, host, lang=lang, content=content, extra_args=extra_args, label=label, **kwargs)
        for evidence in evidences:
            process_evidence(evidence, evidence_saver=evidence_saver)
            yield evidence
    except IssueDoesNotExist:
        print_output("Issue {} does not exist for {}".format(id, host))


def verify(issues, target, *args, **kwargs):
    for host in target:
        for issue in expand_issues(issues):
            yield from verify_host(issue, host, *args, **kwargs)


def export_evidences(evidences, filename):
    with open(filename, 'w') as f:
        json.dump([asdict(evidence) for evidence in evidences if evidence], f, cls=IssueEncoder)


def import_evidences(filename):
    with open(filename) as f:
        return [Evidence(**data) for data in json.load(f, cls=IssueDecoder)]


def get_issue_ids():
    return list(issues.keys()) + list(expansions.keys())


def expand_issue(issue):
    if issue in expansions:
        return expand_issues(expansions[issue])
    else:
        return [issue]


def expand_issues(issues):
    expanded = []
    for issue in issues:
        expanded += expand_issue(issue)
    return expanded


def print_table(rows, separator_size=4, indent=0):
    """
    rows must be a list of 2-tuples
    """
    indent=" "*indent
    first_column_length = max([len(first) for first, _ in rows])
    format_string = "{}{:<" + str(first_column_length) + "}" + " "*separator_size + "{}"
    for first, second in rows:
        print(format_string.format(indent, first, second))


def show_issue_list(args, extra_args):
    done = set()
    print("Issue groups:")
    indent = 4
    for expansion, issue_list in expansions.items():
        print("{}{}:".format(" "*indent, expansion))
        rows = []
        for id in issue_list:
            issue = issues.get(id)
            if not issue:
                # id is a group
                rows.append((id, "Issue group"))
            else:
                description = issue().description or ""
                rows.append((id, description))
            done.add(id)
        print_table(rows, indent=8)

    print()
    print("Other issues")
    rows = []
    for id, issue in issues.items():
        if id in done:
            continue
        description = issue().description or ""
        rows.append((id, description))
    print_table(rows, indent=4)


def get_proxy():
    return os.environ.get('HTTPS_PROXY',
             os.environ.get('HTTP_PROXY', None))


if __name__ == "__main__":
    from . import main
    main()

#!/usr/bin/env python
from dataclasses import asdict
import json
import logging
import sys

from verifier.evidence_savers import evidence_saver
from .issues import issues, expansions, get_issue
from .issues.base import Evidence
from .util import IssueDoesNotExist
from .config import config, configure
from .content_reader import read_content
from .evidence_savers import evidence_savers

# Keep track of whether an evidence has already been printed, so dividers can be included appropriately
printed_evidence = False

def print_output(output_str, issue_id=None):
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
        outputs = issue.verify(**host)
        host = host['host']
    else:
        evidences = issue.verify(host)
    for evidence in evidences:
        evidence.id = id
        evidence.host = host
        evidence.label = label
        evidence.lang = lang
        yield evidence


def process_evidence(evidence: Evidence, evidence_saver=None):
    print_output(evidence.output, evidence.id)
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
        json.dump([asdict(evidence) for evidence in evidences if evidence], f)


def import_evidences(filename):
    with open(filename) as f:
        return [Evidence(**data) for data in json.load(f)]


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


def main():
    import argparse
    import argcomplete
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    def verify_caller(args, extra_args):
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

    def import_caller(args, extra_args):
        if 'save' in args:
            save = args.save or config['DEFAULT'].get('evidence_saver')
        else:
            save = None
        evidence_saver, _ = get_evidence_saver(save, extra_args)
        evidences = import_evidences(args.import_file)
        for evidence in evidences:
            process_evidence(evidence, evidence_saver=evidence_saver)

    def configure_caller(args, extra_args):
        configure()

    parser = argparse.ArgumentParser(description="Generate evidence for standard issues")
    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    verify_parser = subparsers.add_parser("verify", help="Generate evidence for standard issues")
    verify_parser.add_argument("-t", "--target", required=True, nargs='*', help="Targets")
    verify_parser.add_argument("-i", "--issue", required=True, choices=get_issue_ids(), nargs='*', help="Issue id to verify")
    verify_parser.add_argument("-x", "--export-file", help="Export results to file for later import")
    verify_parser.add_argument("-l", "--lang", choices=["en", "nl"], default="en", help="Reporting language")
    verify_parser.add_argument("-c", "--content", help="File with content for the evidences, e.g. request, response, in the format described in the README")
    verify_parser.add_argument("-L", "--label", help="Different label for the location in the issue")
    verify_parser.add_argument("--proxy", nargs='?', help="Use the given proxy server, insert anything to use proxychains")
    verify_parser.set_defaults(func=verify_caller)

    import_parser = subparsers.add_parser("import", help="Import results from file")
    import_parser.add_argument("import_file", help="File to import")
    import_parser.set_defaults(func=import_caller)

    configure_parser = subparsers.add_parser("configure", help="Configure verifier")
    configure_parser.set_defaults(func=configure_caller)


    for p in [verify_parser, import_parser]:
        p.add_argument("-s", "--save", nargs='?', default=argparse.SUPPRESS, choices=evidence_savers.keys(), help="Save the issue using the default issue saver")

    list_issues = subparsers.add_parser("list", help="List all supported issues")
    list_issues.set_defaults(func=show_issue_list)

    argcomplete.autocomplete(parser)
    args, extra_args = parser.parse_known_args()
    args.func(args, extra_args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
from dataclasses import dataclass, asdict
import json
import logging
from .issues import issues, expansions
from .util import IssueDoesNotExist
from .config import config
from .content_reader import read_content

# Keep track of whether an evidence has already been printed, so dividers can be included appropriately
printed_evidence = False


def print_output(output_str, issue_id=None):
    global printed_evidence
    if printed_evidence:
        print('=========================')
    else:
        printed_evidence = True
    if issue_id:
        print(issue_id)
        print('-------------------------')
    print(output_str)


def create_dradis_issue(project_id, standard_issue_id, host, evidence):
    from dradis import Dradis
    api_token = config['DEFAULT']['api_token']
    url = config['DEFAULT']['url']
    dradis = Dradis(api_token, url)
    standard_issue = dradis.get_standard_issue(standard_issue_id)
    issue = dradis.get_issue_by_title(standard_issue['title'], project_id)
    if not issue:
        issue = dradis.create_issue(project_id, standard_issue['content'])
    node = dradis.get_or_create_node(project_id, host)
    dradis.create_evidence(project_id, node['id'], issue['id'], evidence)
    logging.info("Issue successfully created in dradis")


@dataclass
class Evidence:
    id: int
    host: 'typing.Any'
    output: str
    lang: str = "en"
    dradis_node: str = None


def get_issue(id, lang="en", content=None, extra_args=None, **kwargs):
    try:
        issue_class = issues[id.lower()]
        return issue_class(language=lang, content=content, extra_args=extra_args, **kwargs)
    except KeyError:
        raise ValueError(f"Issue {id} does not exist.")


def get_evidence_host(id, host, lang="en", content=None, extra_args=None, dradis_node=None, **kwargs):
    issue = get_issue(id, lang=lang, content=content, extra_args=extra_args, **kwargs)
    if isinstance(host, dict):
        outputs = issue.verify(**host)
        host = host['host']
    else:
        outputs = issue.verify(host)
    for output in outputs:
        yield Evidence(
            id=id,
            host=host,
            dradis_node=dradis_node,
            output=output,
            lang=lang,
        )


def process_evidence(evidence: Evidence, dradis_project_id=None):
    print_output(evidence.output, evidence.id)
    if dradis_project_id:
        issue = get_issue(evidence.id, lang=evidence.lang)
        create_dradis_issue(dradis_project_id, issue.standard_issue_id, evidence.dradis_node or evidence.host, evidence.output)


def verify_host(id, host, dradis_project_id=None, dradis_node=None, lang="en", export_file=None, content=None, extra_args=None, **kwargs):
    try:
        evidences = get_evidence_host(id, host, lang=lang, content=content, extra_args=extra_args, dradis_node=dradis_node, **kwargs)
        for evidence in evidences:
            process_evidence(evidence, dradis_project_id=dradis_project_id)
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


def print_table(rows, separator_size=4):
    """
    rows must be a list of 2-tuples
    """
    first_column_length = max([len(first) for first, _ in rows])
    format_string = "{:<" + str(first_column_length) + "}" + " "*separator_size + "{}"
    for first, second in rows:
        print(format_string.format(first, second))


def show_issue_list(args, extra_args):
    print("Issues:")
    rows = []
    for id, issue in issues.items():
        description = issue().description or ""
        rows.append((id, description))
    print_table(rows)

    print()
    print("Issue groups:")
    rows = []
    for expansion, issue_list in expansions.items():
        rows.append((expansion, ', '.join(issue_list)))
    print_table(rows)


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
        try:
            for evidence in verify(
                    args.issue,
                    args.target,
                    dradis_project_id=args.dradis_project,
                    dradis_node=args.dradis_node,
                    lang=args.lang,
                    proxy=args.proxy,
                    content=content,
                    extra_args=extra_args):
                evidences.append(evidence)
        finally:
            if evidences and args.export_file:
                export_evidences(evidences, args.export_file)

    def import_caller(args, extra_args):
        evidences = import_evidences(args.import_file)
        for evidence in evidences:
            process_evidence(evidence, dradis_project_id=args.dradis_project)

    parser = argparse.ArgumentParser(description="Generate evidence for standard issues")
    subparsers = parser.add_subparsers(dest="command", metavar="command", required=True)
    verify_parser = subparsers.add_parser("verify", help="Generate evidence for standard issues")
    verify_parser.add_argument("-t", "--target", required=True, nargs='*', help="Targets")
    verify_parser.add_argument("-i", "--issue", required=True, choices=get_issue_ids(), nargs='*', help="Issue id to verify")
    verify_parser.add_argument("-x", "--export-file", help="Export results to file for later import")
    verify_parser.add_argument("-l", "--lang", choices=["en", "nl"], default="en", help="Reporting language")
    verify_parser.add_argument("-c", "--content", help="File with content for the evidences, e.g. request, response, in the format described in the README")
    verify_parser.add_argument("-n", "--dradis_node", help="Dradis node to register the issue under")
    verify_parser.add_argument("--proxy", nargs='?', help="Use the given proxy server, insert anything to use proxychains")
    verify_parser.set_defaults(func=verify_caller)

    import_parser = subparsers.add_parser("import", help="Import results from file")
    import_parser.add_argument("import_file", help="File to import")
    import_parser.set_defaults(func=import_caller)

    list_issues = subparsers.add_parser("list", help="List all supported issues")
    list_issues.set_defaults(func=show_issue_list)

    parser.add_argument("-p", "--dradis-project", help="Dradis project to create issue for")

    argcomplete.autocomplete(parser)
    args, extra_args = parser.parse_known_args()
    args.func(args, extra_args)


if __name__ == "__main__":
    main()

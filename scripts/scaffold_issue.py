#!/usr/bin/env python
from os.path import join, dirname, realpath
import verifier.issues
import types
import inspect
from functools import reduce

def camelize(kebab: str) -> str:
    return reduce(lambda x, y: x + y.capitalize(), kebab.split('-'))

dir = dirname(realpath(__file__))
issues_dir = join(dir, '../verifier/issues')
init_file = join(issues_dir, "__init__.py")

verify_functions = {
    "CommandIssue": """
    def postprocess(self, output):
        # Called by self.run_command
        return output

    def verify(self, host):
        output = self.run_command(...)
        yield self.template.format(output)
""",
    "Issue": """
    def verify(self, host):
        ...
        yield self.template.format(output)
"""
}

issue_contents = """\
from .base import {BaseClass}, add_issue, add_expansion

class {IssueClass}({BaseClass}):
    description = "Verifies that ..."
    _template = {{
        "en": "...",
        "nl": "...",
    }}
    {VerifyFunctions}

add_issue('{issue_name}', {IssueClass})
# add_expansion('expansion-name ', [
#     'issue-name',
#     'issue-name1',
# ])
"""

def all_classes_iter():
    for module in dir(verifier.issues):
        module = getattr(verifier.issues, module)
        if isinstance(module, types.ModuleType):
            for name in dir(module):
                c = getattr(module, name)
                if inspect.isclass(c) and issubclass(c, verifier.issues.Issue):
                    yield name, c


def choose_baseclass():
    # issues = list(all_classes_iter())
    issues = [("Issue", verifier.issues.Issue), ("CommandIssue", verifier.issues.CommandIssue)]
    for i, (name, c) in enumerate(issues):
        print("%d: %s" % (i, name))
    index = input("Choose the issue to subclass: (Issue)")
    if not index:
        return "Issue"
    else:
        index = int(index)
        return issues[index][0]

def create_issue(args):
    if args.baseclass:
        baseclass = args.baseclass
    else:
        baseclass = choose_baseclass()
    issueclass = camelize(args.issue_name).capitalize()
    issuefile = join(issues_dir, args.issue_name.replace('-', '_') + ".py")
    
    contents = issue_contents.format(
        BaseClass=baseclass,
        IssueClass=issueclass,
        issue_name=args.issue_name,
        VerifyFunctions=verify_functions[baseclass]
    )
    with open(issuefile, 'w+') as f:
        f.write(contents)

    with open(init_file, 'r') as f:
        old_contents = f.read()

    with open(init_file, 'w') as f:
        new_contents = "from . import {}\n".format(args.issue_name)  + old_contents
        f.write(new_contents)


from argparse_prompt import PromptParser
parser = PromptParser()
parser.add_argument("--baseclass", choices=["CommandIssue", "Issue"], prompt=False)
parser.add_argument("--issue-name")
args = parser.parse_args()

create_issue(args)

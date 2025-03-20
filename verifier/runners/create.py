from .base import Runner as Base
from jinja2 import Template
from pathlib import Path

dir = Path(__file__).parent

def to_pascal_case(s):
    return ''.join([x.capitalize() for x in s.split('-')])

class CreateRunner(Base):
    name = "create"
    help = "Create a new issue"

    def add_arguments(self):
        self.parser.add_argument("-n", "--name", help="Name of the issue, e.g. new-issue")
        self.parser.add_argument("-e", "--expansion", help="Expansion containing the issue, e.g. new-issues")
        self.parser.add_argument("-b", "--base", help="Base of your issue, CommandIssue if you need to run a command, Issue for a generic issue. Alternatively, any of the other existing issues, but take care to import it correctly.", default="CommandIssue")

    def caller(self, args, extra_args):
        if not args.name:
            args.name = input(f"Name of your issue, e.g. new-issue ({args.name}): ")
            args.expansion = input(f"Expansion containing the issue, e.g. new-issues (leave empty for no expansion) ({args.expansion}): ")
            args.base = input(f"Base of your issue, CommandIssue if you need to run a command, Issue for a generic issue. Alternatively, any of the other existing issues, but take care to import it correctly. ({args.base}): ")
            if not args.base:
                args.base = "CommandIssue"
        env = {
            "name": to_pascal_case(args.name),
            "tag": args.name,
            "expansion": args.expansion,
            "base": args.base
        }
        issue_file = env['tag'].replace('-', '_').lower() + ".py"
        try:
            with open(dir.parent.parent / "scaffolding" / "issue.py.j2") as f:
                t = Template(f.read())
        except FileNotFoundError:
            print("Could not find scaffolding directory, did you install Verifier editable?")
            raise
        rendered = t.render(**env)
        issue_path = dir.parent / "issues" / issue_file
        if issue_path.exists():
            print(f"Issue {issue_path.resolve()} already exists")
        else:
            with open(issue_path, 'w') as f:
                f.write(rendered)
            print("Created new issue in", issue_path.resolve())

        
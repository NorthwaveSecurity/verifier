from .base import CommandIssue, add_issue, add_expansion
import re

class Nuclei(CommandIssue):
    description = "Run a curl command without specific issue"
    _template = {
        "en": """Nuclei output:

bc.. {}
        """,
    }
    issues = []

    def postprocess(self, output):
        # Parse all found issues
        for line in output.splitlines():
            matches = re.findall(r"\[[^\]]+\]", line)
            if matches:
                issue_id = matches[1][1:-1]
                self.issues.append(issue_id)
        return output

    def verify(self, host):
        output = self.run_command(
            ["nuclei", "-nc", "-u",  host] + self.extra_args, 
            ["nuclei", "-u",  host] + self.extra_args
        )
        yield self.template.format(output)


add_issue('nuclei', Nuclei)
# add_expansion('expansion-name ', [
#     'issue-name',
#     'issue-name1',
# ])

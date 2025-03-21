from .base import Issue, add_issue, Evidence


class NessusIssue(Issue):
    description = "Default Nessus issue that saves the Nessus plugin output."
    _standard_issue_id = None

    def __init__(self, language="en", content=None, extra_args=None, proxy=None):
        # used when listing all issues, so standard issue id doesn't matter.
        if content is not None:
            self._standard_issue_id = content['nessus']['std_issue_id']
        
        super().__init__(language, content, extra_args, proxy)


    def verify(self, host):
        yield Evidence(output=self.content['nessus']['nessus_output'])

add_issue('nessus', NessusIssue)

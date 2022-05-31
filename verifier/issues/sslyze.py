from .base import CommandIssue, add_expansion, add_issue
from functools import cache
from ..util import SNIP, IssueDoesNotExist, HIGHLIGHT_START, HIGHLIGHT_END

class SSLyzeIssue(CommandIssue):
    description = "Run SSLyze"

    @cache
    def run_sslyze(self, host):
        return super().run_command(["sslyze", host])

    def verify(self, host):
        result = self.run_sslyze(host)
        yield result

add_issue("sslyze", SSLyzeIssue)

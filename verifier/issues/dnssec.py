from .dig import DigIssue
from .base import add_issue, Evidence
from ..util import highlight, IssueDoesNotExist
import re


class DNSSec(DigIssue):
    description = "Verify that DNSSEC is not configured"

    def verify(self, host):
        check_http = re.match(r"^https?://(.*)$", host)
        if check_http:
            host = check_http.group(1)
        command = [host, '+dnssec', '+multi']
        output_str = self.run_command(command)
        regex = r'(?<=;; )flags: .*;'
        flags = re.search(regex, output_str)
        if "ANSWER: 0" in output_str:
            raise Exception("No answer section, did you provide the correct hostname?")
        if 'ad' in flags.group(0):
            raise IssueDoesNotExist()
        output_str = self.postprocess(output_str)
        output_str = highlight(output_str, regex)
        yield Evidence(self.template.format(output_str))


class NSEC(DigIssue):
    description = "Verify that NSEC is configured"

    def verify(self, host):
        command = [host, '+short', "NSEC"]
        output_str = self.run_command(command)
        if output_str.count(host) < 2:
            raise IssueDoesNotExist()
        output_str = self.postprocess(output_str)
        yield Evidence(self.template.format(output_str))


add_issue('dnssec', DNSSec)
add_issue('nsec', NSEC)

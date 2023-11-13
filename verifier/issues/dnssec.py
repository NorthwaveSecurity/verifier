from .dig import DigIssue
from .base import add_issue, Evidence
from ..util import highlight, IssueDoesNotExist
import re


class DNSSec(DigIssue):
    description = "Verify that DNSSEC is not configured"

    def verify(self, host, dns_server="8.8.8.8"):
        command = ['dig', f"@{dns_server}", host, '+dnssec', '+multi']
        regex = r'(?<=;; )flags: .*;'
        output_str = self.run_command(command)
        flags = re.search(regex, output_str)
        if 'ad' in flags.group(0):
            raise IssueDoesNotExist()
        output_str = self.postprocess(output_str)
        output_str = highlight(output_str, regex)
        yield Evidence(self.template.format(output_str))


class NSEC(DigIssue):
    description = "Verify that NSEC is configured"

    def verify(self, host):
        command = ['dig', '+short', "NSEC", host]
        output_str = self.run_command(command)
        if output_str.count(host) < 2:
            raise IssueDoesNotExist()
        output_str = self.postprocess(output_str)
        yield Evidence(self.template.format(output_str))


add_issue('dnssec', DNSSec)
add_issue('nsec', NSEC)

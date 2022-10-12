import argparse
from verifier.util import format_request_response
from .base import add_issue, add_expansion
from .dradis_curl_issue import DradisCurlIssue, format_request_response
from ..util import HIGHLIGHT_START, HIGHLIGHT_END, highlight, truncate_response

class Lfi(DradisCurlIssue):
    description = "Generates evidence for local file inclusion. Usage: verifier verify -i lfi -t https://example.com?file=<filename> -- /etc/passwd. The given filename will be templated into <filename> and highlighted."
    filename = "/etc/passwd"

    def parse_args(self, args):
        if args:
            self.filename = args[0]
        super().parse_args(args[1:])

    def verify(self, host):
        host = host.replace("<filename>", self.filename)
        req, resp = self.do_request(host)
        resp.highlight_body = True
        resp.truncated = 1000
        req = highlight(str(req), self.filename)
        yield format_request_response(req, resp)

add_issue('lfi', Lfi)

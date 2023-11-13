from .base import Issue, add_issue
from dradis_curl import do_request, Request, Response
import argparse
from ..util import SNIP, IssueDoesNotExist, format_request_response
from collections import defaultdict


class DradisCurlIssue(Issue):
    proxies = None
    description = "Run a Dradis curl command without specific issue"
    _template = defaultdict(lambda: """p. Request:

bc.. {}

p. Response:

bc.. {}""")

    def parse_args(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument("--no-redirects", action="store_false", dest="allow_redirects", help="Do not allow redirects")
        self.parsed_args = parser.parse_args(args)

    def edit_body(self, response, edit_function):
        header = response.headers_string
        body = response.text
        new_body = [
            '\r\n',
            SNIP,
        ]
        has_content = False
        for line in body.splitlines():
            new_line = edit_function(line)
            if new_line is not False:
                has_content = True
                new_body.append(new_line)
        if not has_content:
            raise IssueDoesNotExist()
        new_body.append(SNIP)
        return header + '\r\n'.join(new_body)

    def do_request(self, url, *args, **kwargs):
        request = self.content.get('request')
        response = self.content.get('response')
        if request and response:
            return Request(text=request), Response(text=response)
        else:
            kwargs = self.parsed_args.__dict__ | kwargs
            return do_request(url, proxies=self.proxies, *args, **kwargs)

    def handle_proxy(self, proxy):
        self.proxies = dict(http=proxy, https=proxy)

    def verify(self, host):
        req, resp = self.do_request(host)
        evidence = Evidence(output=format_request_response(req, resp))
        evidence.req = req
        evidence.resp = resp
        yield evidence


add_issue('dradis-curl', DradisCurlIssue)

from .base import Issue, add_issue
import re
from ..util import highlight, format_request_response, IssueDoesNotExist


class Cors(Issue):
    description = "Verify that Cors is misconfigured"

    def verify(self, host):
        origin_regex = re.compile(r"(?i)Origin: ([^\r\n]+)")
        access_control_regex = re.compile(r"(?i)Access-Control-Allow-Origin: ([^\r\n]+)")
        if 'request' not in self.content or 'response' not in self.content:
            raise Exception("Content is required for the Cors issue")
        request = self.content['request']
        response = self.content['response']
        origin = re.search(origin_regex, request)
        access_control = re.search(access_control_regex, response)
        if not (origin and access_control) or \
                not (origin.group(1) in access_control.group(1) or access_control.group(1) == '*'):
            raise IssueDoesNotExist()
        request = highlight(request, origin_regex)
        response = highlight(response, access_control_regex)
        yield self.template.format(format_request_response(request, response))


add_issue('cors', Cors)

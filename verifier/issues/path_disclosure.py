from .base import add_issue, Evidence
from .dradis_curl_issue import DradisCurlIssue
from ..util import highlight
import re


class PathDisclosure(DradisCurlIssue):
    description = "Verify that the response discloses a full path"
    path_regex = r'(?<!:/)(?<![A-Za-z])(?:[A-Za-z]:)?[\\/]([^\\/:*?"<>|\r\n]+[\\/])+[^\\/:*?"<>|\r\n ]*'

    def edit(self, response):
        def edit_function(line):
            if re.search(self.path_regex, line):
                return highlight(line, self.path_regex)
            else:
                return False
        return self.edit_body(response, edit_function)

    def verify(self, url):
        request, response = self.do_request(url)
        evidence = Evidence(self.template.format(request, self.edit(response)))
        evidence.request = request
        evidence.response = response
        yield evidence


add_issue('path-disclosure', PathDisclosure)

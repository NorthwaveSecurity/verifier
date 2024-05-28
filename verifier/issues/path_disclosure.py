from .base import add_issue, Evidence
from .dradis_curl_issue import DradisCurlIssue
from ..util import highlight
import re


class PathDisclosure(DradisCurlIssue):
    description = "Verify that the response discloses a full path"
    path_regexes = [
        # Windows
        r'[A-Za-z]:(\\[^/\\<>:"|?*]+){2,}',
        # Unix
        r'(?<!:/)(?<![A-Za-z])(/[^/\\<>:"|?*]+){2,}'
    ]

    def edit(self, response):
        def edit_function(line):
            for regex in self.path_regexes:
                print(regex, line)
                if re.search(regex, line):
                    return highlight(line, regex)
            return False
        return self.edit_body(response, edit_function)

    def verify(self, url):
        request, response = self.do_request(url)
        evidence = Evidence(self.template.format(request, self.edit(response)))
        evidence.request = request
        evidence.response = response
        yield evidence


add_issue('path-disclosure', PathDisclosure)

from .dradis_curl_issue import DradisCurlIssue
from .base import add_issue, Evidence
from ..util import highlight, host_to_url, format_request_response, IssueDoesNotExist
import re


class ServerVersion(DradisCurlIssue):
    _template = {
        "en": """p. Request-response pair:

{}

p. Software: {} version {}.""",
    }
    description = "Verify that the Server HTTP header contains version information"
    software_regex = r'([\w-]+)'
    version_regex = r'([\d\.v]+)'

    def parse_server_header(self, server_header):
        m = re.search(r'{}/{}'.format(self.software_regex, self.version_regex), server_header)
        if not m:
            m = re.search(r'{}\({}\)'.format(self.software_regex, self.version_regex), server_header)
        if not m:
            software = None
            version = None
        else:
            software = m.group(1)
            version = m.group(2)
        return software, version

    def verify(self, url):
        url = host_to_url(url)
        request, response = self.do_request(url, body=False)
        server_header = response.headers.get('Server')
        if not server_header or not re.search(r'\d', server_header):
            raise IssueDoesNotExist()
        self.software, self.version = self.parse_server_header(server_header)
        regex = r'(?i)(?m)^Server: ([^\r\n]+)'
        response = highlight(str(response), regex)
        output_str = format_request_response(request, response)
        evidence = Evidence(self.template.format(output_str, self.software or "TODO", self.version or "TODO"))
        evidence.request = request
        evidence.response = response
        yield evidence


add_issue('server-version', ServerVersion)

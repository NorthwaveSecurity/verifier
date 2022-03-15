from .base import add_issue, add_expansion
from .dradis_curl_issue import DradisCurlIssue
from ..util import host_to_url, highlight, IssueDoesNotExist


class MissingHeader(DradisCurlIssue):
    header = None
    allow_redirects = None

    def check_header(self, response):
        return self.header and self.header in response.headers

    def do_request(self, url):
        url = host_to_url(url)
        allow_redirects = self.allow_redirects if self.allow_redirects is not None else self.parsed_args.allow_redirects
        return super().do_request(url, body=False, allow_redirects=allow_redirects)

    def format_template(self, request, response):
        return self.template.format(request, response, self.header or "mentioned")

    def verify(self, url):
        request, response = self.do_request(url)
        if self.check_header(response):
            raise IssueDoesNotExist()
        yield self.format_template(request, response)

    @property
    def description(self):
        if not self.header:
            return "Verify a missing HTTP header"
        else:
            return "Verify that the HTTP header {} is missing".format(self.header)


class XXSSProtection(MissingHeader):
    header = 'X-XSS-Protection'


class XFrameOptions(MissingHeader):
    header = 'X-Frame-Options'


class XContentTypeOptions(MissingHeader):
    header = 'X-Content-Type-Options'


class StrictTransportSecurity(MissingHeader):
    header = 'Strict-Transport-Security'
    allow_redirects = False


class ContentSecurityPolicy(MissingHeader):
    header = 'Content-Security-Policy'

    def verify(self, url):
        request, response = self.do_request(url)
        triggers = ['unsafe-inline', 'unsafe-eval']
        if self.check_header(response):
            if any([t in response.headers.get(self.header) for t in triggers]):
                response = highlight(str(response), '|'.join(triggers))
            else:
                raise IssueDoesNotExist()
        yield self.format_template(request, response)

    @property
    def description(self):
        return super().description + " or can be stricter"


add_issue('x-xss-protection', XXSSProtection)
add_issue('x-frame-options', XFrameOptions)
add_issue('x-content-type-options', XContentTypeOptions)
add_issue('strict-transport-security', StrictTransportSecurity)
add_issue('content-security-policy', ContentSecurityPolicy)
add_issue('missing-header', MissingHeader)

add_expansion('all-missing-headers', [
    'x-xss-protection',
    'x-frame-options',
    'x-content-type-options',
    'strict-transport-security',
    'content-security-policy',
])

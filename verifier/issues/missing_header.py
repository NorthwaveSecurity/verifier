from .base import add_issue, add_expansion
from .dradis_curl_issue import DradisCurlIssue
from ..util import host_to_url, highlight, IssueDoesNotExist


class MissingHeader(DradisCurlIssue):
    header = None
    allow_redirects = None
    _footer = {
        "en": "Missing header: {}",
        "nl": "Ontbrekende header: {}"
    }
    _template = {
        "en": """p. Request:

bc.. {}

p. Response:

bc.. {}

p. {}.""",
        "nl": """p. Request:

bc.. {}

p. Response:

bc.. {}

p. {}.""",
    }

    def check_header(self, response):
        return self.header and self.header in response.headers

    def do_request(self, url):
        url = host_to_url(url)
        allow_redirects = self.allow_redirects if self.allow_redirects is not None else self.parsed_args.allow_redirects
        return super().do_request(url, body=False, allow_redirects=allow_redirects)

    def footer(self, _footer=None):
        if not _footer:
            _footer = self._footer
        return _footer[self.language].format(self.header or "mentioned")

    def format_template(self, request, response):
        return self.template.format(request, response, self.footer())

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
    _footer_unsafe = {
        "en": "This shows that the {} header contains unsafe directives",
        "nl": "Dit laat zien dat de {} header unsafe directives bevat"
    }
    _footer_frame_ancestors = {
        "en": "This shows that the 'frame-ancestors' directive in the {} header is not set correctly",
        "nl": "Dit toont aan dat het 'frame-ancestors' directive in de {} header niet correct is ingesteld"
    }
    header_present = False
    problem = None

    def check_frame_ancestors(self, response):
        header = response.headers.get(self.header)
        for part in header.split(';'):
            key, _, value = part.strip().partition(' ')
            if key == 'frame-ancestors' and ("'none'" in value or "'self'" in value):
                return True
        return False

    def footer(self):
        match self.problem:
            case "unsafe":
                return super().footer(self._footer_unsafe)
            case "frame_ancestors":
                return super().footer(self._footer_frame_ancestors)
            case "missing":
                return super().footer(self._footer)

    def verify(self, url):
        request, response = self.do_request(url)
        triggers = ['unsafe-inline', 'unsafe-eval']
        if self.check_header(response):
            self.header_present = True
            if any([t in response.headers.get(self.header) for t in triggers]):
                response_str = highlight(str(response), '|'.join(triggers))
                self.problem = "unsafe"
                yield self.format_template(request, response_str)
            if not self.check_frame_ancestors(response):
                self.problem = "frame_ancestors"
                response_str = highlight(str(response), r'Content-Security-Policy:[^\n]+')
                yield self.format_template(request, response_str)
        else:
            self.problem = "missing"
            yield self.format_template(request, response)
        if not self.problem:
            raise IssueDoesNotExist()

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
    'x-content-type-options',
    'strict-transport-security',
    'content-security-policy',
])

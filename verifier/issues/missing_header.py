from .base import add_issue, add_expansion, Evidence
from .dradis_curl_issue import DradisCurlIssue
from ..util import host_to_url, highlight, IssueDoesNotExist


class MissingHeader(DradisCurlIssue):
    header = None
    allow_redirects = None
    _footer = {
        "en": "Missing header: {}",
        "nl": "Ontbrekende header: {}"
    }
    suffix = ""
    _template = {
        "en": """p. Request:

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
        evidence = Evidence(self.format_template(request, response))
        evidence.request = request
        evidence.response = response
        yield evidence


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


class ContentSecurityPolicyUnsafe(ContentSecurityPolicy):
    _footer_unsafe = {
        "en": "The {} header contains unsafe directives",
    }
    _footer_frame_ancestors = {
        "en": "The 'frame-ancestors' directive in the {} header is incorrect",
    }

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

    def verify(self, url):
        request, response = self.do_request(url)
        triggers = ['unsafe-inline', 'unsafe-eval']
        if self.check_header(response):
            if any([t in response.headers.get(self.header) for t in triggers]):
                response_str = highlight(str(response), '|'.join(triggers))
                self.problem = "unsafe"
                evidence = Evidence(self.format_template(request, response_str))
                evidence.problem = self.problem
                yield evidence
            if not self.check_frame_ancestors(response):
                self.problem = "frame_ancestors"
                response_str = highlight(str(response), r'Content-Security-Policy:[^\n]+')
                evidence = Evidence(self.format_template(request, response_str))
                evidence.problem = self.problem
                yield evidence
        else:
            raise IssueDoesNotExist()

    @property
    def description(self):
        return "Content-Security-Policy unsafe"


add_issue('x-xss-protection', XXSSProtection)
add_issue('x-frame-options', XFrameOptions)
add_issue('x-content-type-options', XContentTypeOptions)
add_issue('strict-transport-security', StrictTransportSecurity)
add_issue('content-security-policy-missing', ContentSecurityPolicy)
add_issue('content-security-policy-unsafe', ContentSecurityPolicyUnsafe)
add_issue('missing-header', MissingHeader)

add_expansion('content-security-policy', ['content-security-policy-missing', 'content-security-policy-unsafe'])
add_expansion('all-missing-headers', [
    'x-content-type-options',
    'strict-transport-security',
    'content-security-policy',
    #'x-frame-options' is obsolete since the frame-ancestors directive in content-security-policy
    #'x-xss-protection' is obsolete since it is included in content-security-policy nowadays
])

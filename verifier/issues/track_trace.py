from .base import add_issue, add_expansion
from .dradis_curl_issue import DradisCurlIssue
from ..util import IssueDoesNotExist


class TrackTrace(DradisCurlIssue):
    _template = {
        'en': """p. HTTP method: {}.

Request:

bc.. {}

p. Response:

bc.. {}""",
    }

    def check(self, response):
        failure_codes = [400, 404, 405, 501]
        first_line = response.headers_string.partition('\n')[0]
        for code in failure_codes:
            if str(code) in first_line:
                raise IssueDoesNotExist

    def verify(self, url):
        request, response = self.do_request(url, method=self._method, body=False, allow_redirects=True)
        self.check(response)
        yield self.template.format(self._method, request, response, self._method)

    @property
    def description(self):
        return "Send a {} request".format(self._method)


class Track(TrackTrace):
    _method = "TRACK"


class Trace(TrackTrace):
    _method = "TRACE"


add_issue('track', Track)
add_issue('trace', Trace)
add_expansion('track-trace', ['track', 'trace'])

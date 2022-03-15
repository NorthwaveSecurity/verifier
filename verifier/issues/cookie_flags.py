from .dradis_curl_issue import DradisCurlIssue
from .base import add_issue, add_expansion
from ..util import IssueDoesNotExist
import re


class CookieFlags(DradisCurlIssue):
    cookie_regex = r"Set-Cookie: *([^=]+)=[^;\n]([^\n]*)"
    _template = {
        "en": """Request:

bc.. {}

p. Response:

bc.. {}

p. Cookies without {} flag:
{}""",
    }

    @property
    def description(self):
        return f"Verify that the cookie does not have the {self.cookie_flag} flag set"

    def process_response(self, response):
        self.cookies = []

        def handle_cookie(match):
            cookie = match.group(1)
            flags = match.group(2)
            all = match.group(0)
            if self.cookie_flag in flags:
                return all
            else:
                self.cookies.append(cookie)
                return "$${{" + all + "}}$$"
        return re.sub(self.cookie_regex, handle_cookie, response, flags=re.IGNORECASE)

    def format_cookies(self):
        builder = []
        for c in self.cookies:
            builder.append(f"* {c}")
        return "\n".join(builder)

    def verify(self, url):
        request, response = self.do_request(url, body=False)
        response = self.process_response(str(response))
        if not self.cookies:
            raise IssueDoesNotExist
        yield self.template.format(request, response, self.cookie_flag, self.format_cookies())


class HTTPOnlyFlag(CookieFlags):
    cookie_flag = "HttpOnly"


class SecureFlag(CookieFlags):
    cookie_flag = "Secure"


add_issue('http-only-flag', HTTPOnlyFlag)
add_issue('secure-flag', SecureFlag)

add_expansion('cookie-flags', [
    'http-only-flag',
    'secure-flag',
])

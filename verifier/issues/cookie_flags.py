from .dradis_curl_issue import DradisCurlIssue
from .base import add_issue, add_expansion, Issue
from ..util import IssueDoesNotExist
import re
from ..config import config


class CookieFlags(DradisCurlIssue):
    cookie_regex = r"^([^=]+)=[^;\n](.+)$"
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

        search = re.search(r"Set-Cookie: ([^\n\r]+)", response, flags=re.IGNORECASE)
        if not search:
            raise IssueDoesNotExist()

        def handle_cookie(match):
            cookie = match.group(1)
            flags = match.group(2)
            all = match.group(0)
            if self.cookie_flag in flags:
                return all
            else:
                self.cookies.append(cookie)
                return "$${{" + all + "}}$$"

        new_cookie_header = []
        for cookie in search.group(1).split(','):
            cookie = re.sub(self.cookie_regex, handle_cookie, cookie.strip(), flags=re.IGNORECASE)
            new_cookie_header.append(cookie)
        new_cookie_header = "Set-Cookie: " + ', '.join(new_cookie_header)

        return re.sub(r"Set-Cookie: [^\n\r]+", new_cookie_header, response, flags=re.IGNORECASE)

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

class Cookie_Flags_Browser(CookieFlags):
    cookie_flag = None
    _template = {
        "en": """The following cookies have been found without the {} flag:
{}""",
        "nl": """De volgende cookies zijn gevonden zonder {} flag:
{}""",
    }

    def get_function(self):
        import browser_cookie3
        browser = config.get('cookie_flags', 'browser', fallback=None)
        if browser == "firefox":
            return browser_cookie3.firefox
        else:
            return lambda *_: browser_cookie3.load()

    def check_cookie(self, c):
        """Implement in subclasses"""
        raise NotImplementedError()

    def verify(self, domain):
        cookie_file = config.get('cookie_flags', 'cookie_file', fallback=None)
        get_cookies = self.get_function()
        cj = get_cookies(cookie_file, domain)
        self.cookies = []
        for c in cj:
            if not self.check_cookie(c):
                self.cookies.append(c.name)
        if not self.cookies:
            raise IssueDoesNotExist()
        yield self.template.format(self.cookie_flag, self.format_cookies())


class SecureFlag_Browser(SecureFlag, Cookie_Flags_Browser):
    def check_cookie(self, c):
        return c.secure


class HTTPOnlyFlag_Browser(HTTPOnlyFlag, Cookie_Flags_Browser):
    def check_cookie(self, c):
        return 'HTTPOnly' in c._rest


add_issue('http-only-flag', HTTPOnlyFlag)
add_issue('secure-flag', SecureFlag)
add_issue('secure-flag-browser', SecureFlag_Browser)
add_issue('http-only-flag-browser', HTTPOnlyFlag_Browser)

add_expansion('cookie-flags', [
    'http-only-flag',
    'secure-flag',
])

add_expansion('cookie-flags-browser', [
    'http-only-flag-browser',
    'secure-flag-browser',
])

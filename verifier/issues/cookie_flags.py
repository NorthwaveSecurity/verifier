from .dradis_curl_issue import DradisCurlIssue
from .base import add_issue, add_expansion, Issue, Evidence
from ..util import IssueDoesNotExist
import re
from ..config import config
from ..cookies import Cookie


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

    def check_flag(self, value):
        """ Check if the value is correctly set """
        return bool(value)

    def process_response(self, response):
        self.cookies = {}

        def handle_cookie_header(cookie_header_match):
            cookie = Cookie()
            cookie.load(cookie_header_match.group(2))
            new_cookie_header = []
            for cookie,morsel in cookie.items():
                try:
                    value = morsel[self.cookie_flag.lower()]
                    if not self.check_flag(value):
                        # Flag value is incorrect
                        new_cookie_header.append("$${{" + morsel.OutputString() + "}}$$")
                        self.cookies[cookie] = morsel
                        continue
                except AttributeError as e:
                    print(e)
                    new_cookie_header.append("$${{" + morsel.OutputString() + "}}$$")
                    self.cookies[cookie] = morsel
                    continue
                new_cookie_header.append(morsel.OutputString())

            return cookie_header_match.group(1) + ' '.join(new_cookie_header)

        return re.sub(r"(Set-Cookie: )([^\n\r]+)", handle_cookie_header, response, flags=re.IGNORECASE)

    def format_cookies(self):
        builder = []
        for c in self.cookies.keys():
            builder.append(f"* {c.strip()}")
        return "\n".join(builder)

    def verify(self, url):
        request, response = self.do_request(url, body=False)
        response = self.process_response(str(response))
        if not self.cookies:
            raise IssueDoesNotExist
        evidence = Evidence(self.template.format(request, response, self.cookie_flag, self.format_cookies()))
        evidence.cookies = self.cookies
        yield evidence


class HTTPOnlyFlag(CookieFlags):
    cookie_flag = "HttpOnly"


class SecureFlag(CookieFlags):
    cookie_flag = "Secure"

class Cookie_Flags_Browser(CookieFlags):
    cookie_flag = None
    _template = {
        "en": """The following cookies have been found without the {} flag:
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


class Cookie_Flags_Browser(CookieFlags):
    cookie_flag = None
    _template = {
        "en": """The following cookies have been found without the {} flag:
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
        self.cookies = {}
        for c in cj:
            if not self.check_cookie(c):
                self.cookies[c.name] = c
        if not self.cookies:
            raise IssueDoesNotExist()
        evidence = Evidence(self.template.format(self.cookie_flag, self.format_cookies()))
        evidence.cookies = self.cookies
        yield evidence


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

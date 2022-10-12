#!/usr/bin/env python
import requests
import argparse
from verifier.util import HIGHLIGHT_END, HIGHLIGHT_START, SNIP, format_request_response, host_to_url
from verifier.config import config
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.structures import CaseInsensitiveDict
from os import environ
import re
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

user_agent = config.get('dradis_curl', 'user_agent', fallback='Issue verifier')


class RequestResponse:
    def __init__(self, hide_sensitive=True, show_sensitive_length=0, highlight_body=False, truncated=None):
        self.hide_sensitive=hide_sensitive
        self.highlight_body=highlight_body
        # Truncate after `truncated` characters
        self.truncated=truncated

        # Number of characters at beginning and end of sensitive string to show
        self.show_sensitive_length=show_sensitive_length

    def parse(self, text):
        self.headers_string, _, self.text = text.partition('\n\n')
        self.headers = CaseInsensitiveDict()
        for header in self.headers_string.splitlines():
            if ':' in header:
                key, _, value = header.partition(':')
                self.headers[key] = value.lstrip()

    def __repr__(self):
        string = []

        def replace_func(matchobj):
            value = matchobj.group(2)
            if self.show_sensitive_length is None:
                return matchobj.group(0)
            else:
                return matchobj.group(1) + value[:self.show_sensitive_length] + "[REDACTED]" + value[len(value)-self.show_sensitive_length:] + matchobj.group(3)

        def replace_func1(matchobj):
            return matchobj.group(1) + re.sub(r"([^=;]+=)([^;]*)(;?)", replace_func, matchobj.group(2))

        for header in self.headers_string.splitlines():
            header = re.sub(r"(^Cookie: )(.*)$", replace_func1, header)
            header = re.sub(r"(^Set-Cookie: [^=]+=)([^;]+)()", replace_func, header)
            header = re.sub(r"(^Authorization: \w+ )(.*)()$", replace_func, header)
            string.append(header.rstrip())

        string.append("")
        if self.body:
            chars = 0
            should_break = False
            for line in self.text.strip().splitlines():
                if self.truncated and chars + len(line) > self.truncated:
                    line = line[:self.truncated - len(line) - chars]
                    should_break = True
                if self.highlight_body:
                    new_line = HIGHLIGHT_START + line + HIGHLIGHT_END
                else:
                    new_line = line
                string.append(new_line)
                chars += len(line)
                if should_break:
                    string.append(SNIP)
                    break
        return '\r\n'.join(string).rstrip()


class Request(RequestResponse):
    def __init__(self, req=None, text=None, body=True, **kwargs):
        self._req = req
        self.body = body

        if req is not None:
            # Cut off protocol part
            split_url = self._req.url.split("/")
            self.url = '/' + '/'.join(split_url[3:])

            self.host = split_url[2]
            self.headers_string = '{} HTTP/1.1\r\n{}{}'.format(
                self.method + ' ' + self.url,
                f"Host: {self.host}\r\n",
                '\r\n'.join('{}: {}'.format(k, v) for k, v in self.headers.items()))
            self.text = req.body or ""
        elif text:
            self.parse(text)
            self.host = self.headers.get('host')
            self.url = self.headers_string.partition('\r\n')[0].split()[1]

        super().__init__(**kwargs)

    def __getattr__(self, key):
        return getattr(self._req, key)


class Response(RequestResponse):
    def __init__(self, resp=None, text=None, body=True, **kwargs):
        self._resp = resp
        self.body = body

        if resp is not None:
            self.req = Request(req=resp.request, body=body, **kwargs)
            self.headers_string = 'HTTP/1.1 {} {}\r\n{}\r\n\r\n'.format(
                self.status_code, self.reason,
                '\r\n'.join('{}: {}'.format(k, v) for k, v in self.headers.items())
            )
        elif text:
            self.parse(text)

        super().__init__(**kwargs)

    def __getattr__(self, key):
        return getattr(self._resp, key)


def dradis_format(resp, body=True, no_hide=False):
    if no_hide:
        resp = Response(resp=resp, body=body, show_sensitive_length=None)
    else:
        resp = Response(resp=resp, body=body)
    req = resp.req
    return req, resp


def get_headers(headers=None):
    """
    Merge given headers with default
    """
    if not headers:
        headers = {}
    default = {
        "User-Agent": user_agent
    }
    if 'COOKIE' in environ:
        default['Cookie'] = environ['COOKIE']
    for k, v in headers.items():
        default[k] = v
    return default


def do_request(url, method="GET", verify=False, allow_redirects=False, headers=None, proxies=None, timeout=1, *args, **kwargs):
    url = host_to_url(url)
    r = requests.request(method, url, verify=verify, allow_redirects=allow_redirects, headers=get_headers(headers), proxies=proxies, timeout=timeout)
    return dradis_format(r, *args, **kwargs)


def print_request(*args, format='dradis', **kwargs):
    req, resp = do_request(*args, **kwargs)
    string = format_request_response(req, resp, format=format)
    print(string)


def main():
    parser = argparse.ArgumentParser(description="Curl alternative with dradis-format output")
    parser.add_argument('--method', '-m', help="HTTP method", default="GET")
    parser.add_argument('--no-verify', '-k', action="store_false", help="Do not verify", dest="verify")
    parser.add_argument('--no-body', '-n', action="store_false", help="Do not print the body", dest="body")
    parser.add_argument('--format', choices=['dradis', 'verifier'], help="Set the output format")
    parser.add_argument('--no-hide', action="store_true", help="Do not hide sensitive values")
    parser.add_argument('url', help="The url to access")
    args = parser.parse_args()
    print_request(args.url, method=args.method, body=args.body, verify=args.verify, format=args.format, no_hide=args.no_hide)


if __name__ == "__main__":
    main()

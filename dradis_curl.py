#!/usr/bin/env python
import requests
import argparse
from verifier.util import format_request_response, host_to_url
from verifier.config import config
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.structures import CaseInsensitiveDict
from os import environ
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

user_agent = config.get('dradis_curl', 'user_agent', fallback='Issue verifier')


class RequestResponse:
    def parse(self, text):
        self.headers_string, _, self.text = text.partition('\n\n')
        self.headers = CaseInsensitiveDict()
        for header in self.headers_string.splitlines():
            if ':' in header:
                key, _, value = header.partition(':')
                self.headers[key] = value.lstrip()

    def __repr__(self):
        string = self.headers_string.rstrip()
        if self.body:
            string += "\r\n\r\n" + self.text.lstrip()
        return string.rstrip()


class Request(RequestResponse):
    def __init__(self, req=None, text=None, body=True):
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

    def __getattr__(self, key):
        return getattr(self._req, key)


class Response(RequestResponse):
    def __init__(self, resp=None, text=None, body=True):
        self._resp = resp
        self.body = body

        if resp is not None:
            self.req = Request(req=resp.request, body=body)
            self.headers_string = 'HTTP/1.1 {} {}\r\n{}\r\n\r\n'.format(
                self.status_code, self.reason,
                '\r\n'.join('{}: {}'.format(k, v) for k, v in self.headers.items())
            )
        elif text:
            self.parse(text)

    def __getattr__(self, key):
        return getattr(self._resp, key)


def dradis_format(resp, body=True):
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
    parser.add_argument('url', help="The url to access")
    args = parser.parse_args()
    print_request(args.url, method=args.method, body=args.body, verify=args.verify, format=args.format)


if __name__ == "__main__":
    main()

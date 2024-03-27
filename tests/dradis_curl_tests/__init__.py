import unittest
from dradis_curl import Request, Response
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


request_text = """GET / HTTP/1.1
Host: example.com
User-Agent: Issue verifier
Accept-Encoding: gzip, deflate, br, zstd
Accept: */*
Connection: keep-alive

body
"""

response_text = """HTTP/1.1 403 Forbidden
Date: Wed, 27 Mar 2024 09:07:31 GMT
Server: Apache
Content-Length: 199
Keep-Alive: timeout=5, max=100
Connection: Keep-Alive
Content-Type: text/html; charset=iso-8859-1

body
"""

class DradisCurlTest(unittest.TestCase):

    def test_dradis_curl_parsing(self):
        request = Request(text=request_text)
        response = Response(text=response_text)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.reason, "Forbidden")
        self.assertFalse(response.ok)


if __name__ == '__main__':
    unittest.main()

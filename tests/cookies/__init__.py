import unittest
from verifier.content_reader import read_content
from verifier.cookies import Cookie
from dradis_curl import Response
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class CookieParseTest(unittest.TestCase):

    def test_cookie_parsing(self):
        content = read_content(join(dir, 'response.txt'))
        resp = Response(text=content['response'])
        cookies = Cookie(resp.headers['set-cookie'])
        self.assertEqual(str(cookies), "a=xyz; expires=Wednesday, 09-Nov-1999 23:12:40 GMT; Path=/; Secure, b=xyz; expires=Wednesday, 09-Nov-1999 23:12:40 GMT; Path=/; Secure, c=xyz; expires=Wednesday, 09-Nov-1999 23:12:40 GMT; Path=/, d=xyz; expires=Wednesday, 09-Nov-1999 23:12:40 GMT; Path=/; Secure")
        self.assertEqual(len(cookies.values()), 4)


    def test_redact(self):
        content = read_content(join(dir, 'response.txt'))
        resp = Response(text=content['response'])
        resp = Response(text=str(resp)) # Parse the redacted response again
        cookies = resp.headers['set-cookie']        
        self.assertNotIn("xyz", cookies)
        


if __name__ == '__main__':
    unittest.main()

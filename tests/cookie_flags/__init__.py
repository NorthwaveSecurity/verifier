import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class CookieFlagsTest(unittest.TestCase):

    def test_cookie_flags(self):
        content = read_content(join(dir, 'google.com.txt'))
        evidences = verify(['cookie-flags'], ['google.com'], content=content)
        cookies = set(['dwac_1aeb1113dd96a289184864dcce','cqcid', 'cquid', 'sid', '__cq_dnt', 'dw_dnt', 'cc-nx-g_Global', 'cc-sg_Global', '_Locale', 'somepersonalization', 'something', 'Version', 'another_cookie'])

        for evidence in evidences:
            for cookie in evidence.cookies:
                self.assertIn(cookie, cookies)


if __name__ == '__main__':
    unittest.main()

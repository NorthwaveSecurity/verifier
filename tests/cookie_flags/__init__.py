import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class CookieFlagsTest(unittest.TestCase):

    def test_cookie_flags(self):
        content = read_content(join(dir, 'google.com.txt'))
        list(verify(['cookie-flags'], ['google.com'], content=content))


if __name__ == '__main__':
    unittest.main()

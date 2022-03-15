import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class DnssecTest(unittest.TestCase):

    def test_dnssec_nsec(self):
        content = read_content(join(dir, 'google.com'))
        list(verify(['dnssec', 'nsec'], ['google.com'], content=content))


if __name__ == '__main__':
    unittest.main()

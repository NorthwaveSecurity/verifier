import unittest
from verifier.content_reader import read_content
from verifier.verifier import get_evidence_host
from os.path import join, dirname, realpath
from util import print_evidence

dir = dirname(realpath(__file__))


class DnssecTest(unittest.TestCase):

    def test_dnssec_nsec(self):
        content = read_content(join(dir, 'google.com'))
        for issue in ['dnssec', 'nsec']:
            print_evidence(get_evidence_host(issue, 'google.com', content=content))


if __name__ == '__main__':
    unittest.main()

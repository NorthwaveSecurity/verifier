import unittest
from verifier.verifier import get_evidence_host
from os.path import dirname, realpath
from util import print_evidence

dir = dirname(realpath(__file__))


class LfiTest(unittest.TestCase):

    def test_lfi(self):
        print_evidence(get_evidence_host('lfi', 'https://ifconfig.co?file=<filename>', extra_args=['/etc/passwd']))


if __name__ == '__main__':
    unittest.main()

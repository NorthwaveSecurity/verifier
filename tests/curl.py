import unittest
from verifier.verifier import get_evidence_host
from .util import print_evidence


class CurlTest(unittest.TestCase):
    test_site = 'https://ifconfig.co'

    def test_curl(self):
        print_evidence(get_evidence_host('curl', self.test_site))

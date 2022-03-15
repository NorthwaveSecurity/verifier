import unittest
from verifier.verifier import verify_host


class CurlTest(unittest.TestCase):
    test_site = 'https://ifconfig.co'

    def test_curl(self):
        list(verify_host('curl', self.test_site))

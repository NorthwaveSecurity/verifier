import unittest
from verifier.content_reader import read_content
from verifier.verifier import get_evidence_host
from util import print_evidence
import os

dir = os.path.dirname(os.path.realpath(__file__))


class OutdatedTest(unittest.TestCase):

    def test_outdated_jquery(self):
        content = read_content(os.path.join(dir, 'jquery.js'))
        print_evidence(get_evidence_host('outdated-jquery', 'https://code.jquery.com/jquery-1.12.4.js', content=content))

    def test_outdated_wordpress(self):
        content = read_content(os.path.join(dir, 'wordpress.txt'))
        print_evidence(get_evidence_host('outdated-wordpress', 'https://example.com/', content=content))

    def test_outdated_vsftpd(self):
        content = read_content(os.path.join(dir, 'vsftpd.txt'))
        print_evidence(get_evidence_host('outdated-vsftpd', 'example.com', content=content))

    def test_outdated_nginx(self):
        content = read_content(os.path.join(dir, 'nginx.txt'))
        print_evidence(get_evidence_host('outdated-nginx', 'example.com', content=content))

    def test_outdated_iis(self):
        content = read_content(os.path.join(dir, 'iis.txt'))
        print_evidence(get_evidence_host('outdated-iis', 'example.com', content=content))


if __name__ == '__main__':
    unittest.main()

import unittest
from verifier.content_reader import read_content
from verifier.verifier import get_evidence_host
from os.path import join, dirname, realpath
from util import print_evidence

dir = dirname(realpath(__file__))


class HttpLinks(unittest.TestCase):

    def test_http_links(self):
        content = read_content(join(dir, 'example.com.txt'))
        print_evidence(get_evidence_host('http-links', 'example.com', content=content))


if __name__ == '__main__':
    unittest.main()

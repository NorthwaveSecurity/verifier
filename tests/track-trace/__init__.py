import unittest
from verifier.content_reader import read_content
from verifier.verifier import get_evidence_host
from os.path import join, dirname, realpath
from util import print_evidence

dir = dirname(realpath(__file__))


class TrackTraceTest(unittest.TestCase):

    def test_track(self):
        content = read_content(join(dir, 'track.txt'))
        print_evidence(get_evidence_host('track', 'example.com', content=content))

    def test_trace(self):
        content = read_content(join(dir, 'trace.txt'))
        print_evidence(get_evidence_host('trace', 'example.com', content=content))


if __name__ == '__main__':
    unittest.main()

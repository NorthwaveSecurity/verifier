import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class TrackTraceTest(unittest.TestCase):

    def test_track(self):
        content = read_content(join(dir, 'track.txt'))
        list(verify(['track-trace'], ['example.com'], content=content))

    def test_trace(self):
        content = read_content(join(dir, 'trace.txt'))
        list(verify(['track-trace'], ['example.com'], content=content))


if __name__ == '__main__':
    unittest.main()

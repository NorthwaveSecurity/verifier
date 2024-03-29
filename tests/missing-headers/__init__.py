import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class MissingHeadersTest(unittest.TestCase):

    def test_missing_headers(self):
        content = read_content(join(dir, 'example.com.txt'))
        list(verify(['all-missing-headers'], ['example.com'], content=content))

    def test_missing_frame_ancestors(self):
        content = read_content(join(dir, 'missing-frame-ancestors.txt'))
        list(verify(['content-security-policy'], ['example.com'], content=content))


if __name__ == '__main__':
    unittest.main()

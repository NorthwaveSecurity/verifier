import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class PathDisclosureTest(unittest.TestCase):

    def test_path_disclosure(self):
        content = read_content(join(dir, 'example.com.txt'))
        list(verify(['path-disclosure'], ['example.com'], content=content))


if __name__ == '__main__':
    unittest.main()

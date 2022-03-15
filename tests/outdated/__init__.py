import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify_host
import os

dir = os.path.dirname(os.path.realpath(__file__))


class OutdatedTest(unittest.TestCase):

    def test_outdated_jquery(self):
        content = read_content(os.path.join(dir, 'jquery.js'))
        list(verify_host('outdated-jquery', 'https://code.jquery.com/jquery-1.12.4.js', content=content))

    def test_outdated_wordpress(self):
        content = read_content(os.path.join(dir, 'wordpress.txt'))
        list(verify_host('outdated-wordpress', 'https://example.com/', content=content))


if __name__ == '__main__':
    unittest.main()

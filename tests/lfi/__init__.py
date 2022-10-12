import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class LfiTest(unittest.TestCase):

    def test_lfi(self):
        list(verify(['lfi'], ['https://ifconfig.co?file=<filename>'], extra_args=['/etc/passwd']))


if __name__ == '__main__':
    unittest.main()

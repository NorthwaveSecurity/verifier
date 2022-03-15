import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class StacktraceTest(unittest.TestCase):

    def test_stacktrace(self):
        content = read_content(join(dir, 'example.com.txt'))
        list(verify(['stacktrace'], ['example.com'], content=content))


if __name__ == '__main__':
    unittest.main()

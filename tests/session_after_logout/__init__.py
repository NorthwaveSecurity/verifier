import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class SessionafterlogoutTest(unittest.TestCase):

    def test_session_after_logout(self):
        content = read_content(join(dir, 'example.com.txt'))
        list(verify(['session-after-logout'], ['example.com'], content=content))


if __name__ == '__main__':
    unittest.main()

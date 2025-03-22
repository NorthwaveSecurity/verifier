import unittest
from verifier.util import highlight, HIGHLIGHT_END, HIGHLIGHT_START

class HighlightingTest(unittest.TestCase):
    def test_with_whitespace(self):
        string = "   test    "
        self.assertEqual(highlight(string), "   " + HIGHLIGHT_START + "test" + HIGHLIGHT_END + "    ")

    def test_with_line_whitespace(self):
        string = "   test    \r\n"
        self.assertEqual(highlight(string), "   " + HIGHLIGHT_START + "test" + HIGHLIGHT_END + "    \r\n")
        string = "   test    \n"
        self.assertEqual(highlight(string), "   " + HIGHLIGHT_START + "test" + HIGHLIGHT_END + "    \n")
        string = "   test    \r"
        self.assertEqual(highlight(string), "   " + HIGHLIGHT_START + "test" + HIGHLIGHT_END + "    \r")

    def test_with_whitespace_in_between(self):
        string = "   test abc    "
        self.assertEqual(highlight(string), "   " + HIGHLIGHT_START + "test abc" + HIGHLIGHT_END + "    ")

    def test_without_whitespace(self):
        string = "test abc"
        self.assertEqual(highlight(string), HIGHLIGHT_START + "test abc" + HIGHLIGHT_END)

        string = "test"
        self.assertEqual(highlight(string), HIGHLIGHT_START + "test" + HIGHLIGHT_END)

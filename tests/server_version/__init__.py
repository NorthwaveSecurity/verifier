import unittest
from verifier.issues.server_version import ServerVersion
from verifier.content_reader import read_content
from verifier.util import IssueDoesNotExist
import os


dir = os.path.dirname(os.path.realpath(__file__))


class TestServerVersion(unittest.TestCase):

    def run_test(self, filename):
        content = read_content(os.path.join(dir, filename))
        issue = ServerVersion(content=content)
        result = issue.verify("example.com")
        return issue, next(result)

    def test_apache(self):
        issue, result = self.run_test('apache.txt')
        self.assertEqual(issue.software, "Apache")
        self.assertEqual(issue.version, "2.4.29")

    def test_jetty(self):
        issue, result = self.run_test('jetty.txt')
        self.assertEqual(issue.software, "Jetty")
        self.assertEqual(issue.version, "9.2.9.v20150224")

    def test_microsoft(self):
        issue, result = self.run_test('microsoft.txt')
        self.assertEqual(issue.software, "Microsoft-IIS")
        self.assertEqual(issue.version, "7.0")

    def test_unknown(self):
        issue, result = self.run_test('unknown.txt')
        self.assertIsNone(issue.software)
        self.assertIsNone(issue.version)

    def test_not_exist(self):
        self.assertRaises(IssueDoesNotExist, lambda: self.run_test("not_exist.txt"))
        self.assertRaises(IssueDoesNotExist, lambda: self.run_test("not_exist1.txt"))


if __name__ == '__main__':
    unittest.main()

import unittest
from verifier import expand_issue, expand_issues, expansions

class ExpansionTest(unittest.TestCase):

    def test_expand_all(self):
        expanded = expand_issue('all')
        self.assertGreater(len(expanded), len(expansions.get('all')))
        expanded1 = expand_issues(['all'])
        self.assertEqual(expanded, expanded1)

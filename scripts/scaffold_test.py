#!/usr/bin/env python
from os.path import join, dirname, realpath
import verifier.issues
from scaffold_issue import camelize
import os

dir = dirname(realpath(__file__))
tests_dir = join(dir, '../tests')

issue_contents = """\
import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class {TestClass}Test(unittest.TestCase):

    def test_{test_name}(self):
        content = read_content(join(dir, '{domain}.txt'))
        list(verify(['{issue_name}'], ['{domain}'], content=content))


if __name__ == '__main__':
    unittest.main()
"""


def create_test(args):
    testclass = camelize(args.issue_name).capitalize()
    test_name = args.issue_name.replace('-', '_')
    domain = "example.com"
    dir = join(tests_dir, args.issue_name.replace('-', '_'))
    test_file = join(dir, "__init__.py")
    input_file = join(dir, domain + ".txt")
    
    contents = issue_contents.format(
        TestClass=testclass,
        issue_name=args.issue_name,
        test_name=test_name,
        domain=domain,
    )
    os.makedirs(dir)
    with open(test_file, 'w+') as f:
        f.write(contents)
    with open(input_file, 'w+') as f:
        pass



if __name__ == "__main__":
    from argparse_prompt import PromptParser
    parser = PromptParser()
    parser.add_argument("--issue-name")
    args = parser.parse_args()

    create_test(args)

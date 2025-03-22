import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify, get_evidence_host
from os.path import join, dirname, realpath
from util import print_evidence

dir = dirname(realpath(__file__))


class MissingHeadersTest(unittest.TestCase):

    def test_missing_headers(self):
        content = read_content(join(dir, 'example.com.txt'))
        results = list(verify([
            'x-xss-protection',
            'x-frame-options',
            'x-content-type-options',
            'content-security-policy'
        ] , ['example.com'], content=content))
        for r in results:
            self.assertNotIn("over HTTPS", str(r))

    def test_hsts(self):
        content = read_content(join(dir, 'example.com.txt'))
        results = list(verify(['strict-transport-security'], ['example.com'], content=content))
        print_evidence(results)

    def test_missing_frame_ancestors(self):
        content = read_content(join(dir, 'missing-frame-ancestors.txt'))
        print_evidence(get_evidence_host('content-security-policy-unsafe', 'example.com', content=content))

    def test_unsafe_csp(self):
        content = read_content(join(dir, 'unsafe-csp.txt'))
        print_evidence(get_evidence_host('content-security-policy-unsafe', 'example.com', content=content))
        

if __name__ == '__main__':
    unittest.main()

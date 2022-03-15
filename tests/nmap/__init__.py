import unittest
from verifier.content_reader import read_content
from verifier.verifier import verify_host
from os.path import join, dirname, realpath

dir = dirname(realpath(__file__))


class NmapTest(unittest.TestCase):

    def test_dns_cache_snoop(self):
        content = read_content(join(dir, 'dns-cache-snoop.txt'))
        list(verify_host('dns-cache-snoop', '8.8.8.8', content=content))

    def test_dns_recursion(self):
        content = read_content(join(dir, 'dns-recursion.txt'))
        list(verify_host('dns-recursion', '8.8.8.8', content=content))

    def test_outdated_msdns(self):
        content = read_content(join(dir, 'outdated-msdns.txt'))
        list(verify_host('outdated-msdns', '10.10.10.100', content=content))

    def test_smb_signing(self):
        content = read_content(join(dir, 'smb-signing.txt'))
        list(verify_host('smb-signing', '192.168.60.2', content=content))


if __name__ == '__main__':
    unittest.main()

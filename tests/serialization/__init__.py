import unittest
import tempfile
import os
import json
from os.path import join, dirname, realpath
from verifier.verifier import export_evidences, import_evidences
from verifier.content_reader import read_content
from verifier.verifier import verify


dir = dirname(realpath(__file__))


class SerializationTests(unittest.TestCase):

    def setUp(self) -> None:
        self.outfile_path = tempfile.mkstemp(suffix='.json')[1]
        content = read_content(join(dir, 'example.com.txt'))
        self.evidences = list(verify(['strict-transport-security'], ['example.com'], content=content))
        return super().setUp()
    
    def tearDown(self) -> None:
        try:
            os.remove(self.outfile_path)
        except:
            pass
        return super().tearDown()

    def test_export_evidences(self):
        export_evidences(self.evidences, self.outfile_path)        

    def test_import_evidences(self):
        self.maxDiff = None        
        imported_evidences = import_evidences(join(dir, 'import.json'))

        
        self.assertListEqual(self.evidences, imported_evidences)


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

        imported_evidence = imported_evidences[0]
        generated_evidence = self.evidences[0]

        self.assertEqual(generated_evidence.output, imported_evidence.output)
        self.assertEqual(generated_evidence.issue_id, imported_evidence.issue_id)
        self.assertEqual(generated_evidence.host, imported_evidence.host)
        self.assertEqual(generated_evidence.lang, imported_evidence.lang)
        self.assertEqual(generated_evidence.label, imported_evidence.label)

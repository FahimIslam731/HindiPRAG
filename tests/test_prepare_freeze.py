import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('freeze', ROOT / 'scripts/prepare_freeze.py')
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)
class FreezeTest(unittest.TestCase):
    def test_missing_evidence_stays_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'inventory'; result = f.prepare(path)
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertIsNone(result['denominators']['jra'])
            flags = [json.loads(x) for x in (path/'eligibility.jsonl').read_text().splitlines()]
            self.assertEqual(len(flags), 200)
            self.assertTrue(all(x['jra_eligible'] is None and x['sc_eligible'] is None for x in flags))
            self.assertEqual(result['outputs']['families.jsonl'], f.sha(path/'families.jsonl'))
            with self.assertRaises(FileExistsError): f.prepare(path)

import importlib.util
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('split', ROOT / 'scripts/create_splits.py')
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
class SplitsTest(unittest.TestCase):
    def test_determinism_and_no_leakage(self):
        records = [json.loads(x) for x in s.DATA.read_text().splitlines() if x.strip()]
        split, subset = s.build(records)
        self.assertEqual((split, subset), s.build(records))
        buckets = split['splits']; self.assertEqual([len(buckets[k]) for k in ('train','validation','test')], [120,30,50])
        allocation = {fid: name for name, values in buckets.items() for fid in values}
        self.assertEqual(len(allocation), 200)
        self.assertTrue({f'F{i:03}' for i in range(1,25)} <= set(buckets['train']))
        self.assertEqual(allocation['F029'], 'train')
        groups = {}
        for row in records: groups.setdefault(row['template_group_id'], set()).add(allocation[row['family_id']])
        self.assertTrue(all(len(v) == 1 for v in groups.values()))
        for a,b in s.LINKS: self.assertEqual(allocation[a], allocation[b])
        self.assertEqual(len(subset['family_ids']), 30)
        self.assertTrue(set(subset['family_ids']) <= set(buckets['test']))

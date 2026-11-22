import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('freeze_release', ROOT/'scripts/freeze_release.py')
f = importlib.util.module_from_spec(spec); spec.loader.exec_module(f)

class ReleaseGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.dir = Path(self.temp.name)
        self.policy = self.dir/'policy.json'; self.votes = self.dir/'votes.csv'
        families = [json.loads(x) for x in (ROOT/'data/draft/families.jsonl').read_text().splitlines()]
        self.splits = json.loads((ROOT/'data/splits.json').read_text())['splits']
        self.policy.write_text(json.dumps({'version':'fixture-only', 'approved_by':'synthetic', 'approval_evidence':'test', 'pairwise_instructions':'test', 'independence_evidence':'test', 'pairs':{r['family_id']:['A','B'] for r in families}}))
        fields = ['family_id','audience','phrasing','left_id','right_id','outcome','annotator_id','rationale']
        self.rows = []
        for family in families:
            fid = family['family_id']; count = 2 if fid not in self.splits['train'] or int(fid[1:]) <= 24 else 1
            for a,p in f.CONTEXTS:
                for i in range(count):
                    self.rows.append(dict(zip(fields,[fid,a,p,'A','B','left' if a == 'familiar' else 'right',f'fixture{i}','synthetic'])))
        self.fields = fields; self.write_votes()
    def tearDown(self): self.temp.cleanup()
    def write_votes(self):
        with self.votes.open('w', newline='') as h:
            w=csv.DictWriter(h, fieldnames=self.fields); w.writeheader(); w.writerows(self.rows)
    def test_synthetic_complete_release_and_checksums(self):
        out=self.dir/'out'; result=f.release(out,'test-v1',self.policy,[self.votes])
        self.assertEqual(result['status'],'FROZEN'); self.assertEqual(result['denominators']['test']['jra'],50)
        self.assertEqual(result['denominators']['test']['sc'],50)
        for name,digest in result['files_sha256'].items(): self.assertEqual(f.sha(out/name),digest)
        with self.assertRaises(FileExistsError): f.release(out,'test-v1',self.policy,[self.votes])
    def test_missing_vote_blocks_without_output(self):
        self.rows.pop(); self.write_votes(); out=self.dir/'out'
        result=f.release(out,'v1',self.policy,[self.votes]); self.assertEqual(result['status'],'BLOCKED')
        self.assertTrue(result['missing_contexts']); self.assertFalse(out.exists())
    def test_tie_excluded_and_no_paraphrase_consistency(self):
        # A single training reviewer can report a tie; this is not a missing label.
        index = next(i for i,r in enumerate(self.rows) if r['family_id']=='F030' and r['audience']=='familiar' and r['phrasing']=='scenario')
        self.rows[index]['outcome']='tie'; self.write_votes()
        result=f.evaluate(self.policy,[self.votes]); flag=next(x for x in result['flags'] if x['family_id']=='F030')
        self.assertFalse(flag['jra_eligible']); self.assertFalse(flag['sc_eligible'])
        self.assertEqual(flag['jra_exclusion_reasons'],['originals_not_strict_reversal'])
    def test_disagreement_requires_real_adjudication(self):
        index=next(i for i,r in enumerate(self.rows) if r['family_id']=='F001' and r['annotator_id']=='fixture1')
        self.rows[index]['outcome']='tie'; self.write_votes()
        result=f.release(self.dir/'out','v1',self.policy,[self.votes])
        self.assertEqual(result['status'],'BLOCKED'); self.assertTrue(result['unresolved_contexts'])
    def test_adjudication_resolves_disagreement(self):
        index=next(i for i,r in enumerate(self.rows) if r['family_id']=='F001' and r['audience']=='familiar' and r['phrasing']=='scenario' and r['annotator_id']=='fixture1')
        self.rows[index]['outcome']='tie'; self.write_votes()
        path=self.dir/'adjudication.csv'; fields=self.fields+['source_reviewers']
        with path.open('w', newline='') as h:
            w=csv.DictWriter(h, fieldnames=fields); w.writeheader()
            w.writerow(dict(self.rows[index], outcome='left', annotator_id='third', source_reviewers='fixture0|fixture1'))
        result=f.evaluate(self.policy,[self.votes],[path])
        self.assertFalse(result['unresolved']); self.assertTrue(next(x for x in result['flags'] if x['family_id']=='F001')['jra_eligible'])
    def test_paraphrase_changes_sc_not_jra(self):
        indices=[i for i,r in enumerate(self.rows) if r['family_id']=='F030' and r['audience']=='familiar' and r['phrasing']=='paraphrase']
        for i in indices: self.rows[i]['outcome']='right'
        self.write_votes(); result=f.evaluate(self.policy,[self.votes]); flag=next(x for x in result['flags'] if x['family_id']=='F030')
        self.assertTrue(flag['jra_eligible']); self.assertFalse(flag['sc_eligible'])
    def test_missing_policy_pair_fails(self):
        policy=json.loads(self.policy.read_text()); del policy['pairs']['F001']; self.policy.write_text(json.dumps(policy))
        with self.assertRaisesRegex(ValueError,'explicit pair'): f.evaluate(self.policy,[self.votes])

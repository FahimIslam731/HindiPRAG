import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import annotations
import blind_annotation_packets as blind
import prepare_annotation_packets as packets
import unblind_annotation_packet as unblind

class BlindPacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.b=self.base/'blind';self.m=self.base/'map'
        source=self.base/'packets'; packets.write_packets(source)
        blind.generate(self.b,self.m,source)
    def tearDown(self): self.tmp.cleanup()
    def read(self,p):
        with p.open(newline='',encoding='utf-8') as h:
            r=csv.DictReader(h);return r.fieldnames,list(r)
    def write(self,p,fields,rows):
        with p.open('w',newline='',encoding='utf-8') as h:
            w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
    def test_aliases_change_across_prompts_and_roundtrip_to_importer(self):
        mapping_path=self.m/'reviewer_1_crosswalk.csv'; _,crosswalk=self.read(mapping_path)
        self.assertEqual({r['candidate_id'] for r in crosswalk if r['display_id']=='X1'},{'A','B','C'})
        pref=self.b/'reviewer_1_preferences.csv'; rating=self.b/'reviewer_1_candidate_ratings.csv'
        fields,rows=self.read(pref);row=rows[0]
        row.update(preferred_candidate_id='tie', tied_candidate_ids='X1|X3',decision_rationale='synthetic fixture',annotator_id='fixture')
        self.write(pref,fields,rows)
        rf,rr=self.read(rating)
        for r in rr:
            if (r['family_id'],r['audience'],r['phrasing'])==(row['family_id'],row['audience'],row['phrasing']):
                r.update(meaning_fidelity='pass',register_fit='appropriate',naturalness_1_to_5='4',annotator_id='fixture')
        self.write(rating,rf,rr)
        out=self.base/'out'; unblind.convert(pref,rating,mapping_path,out)
        report=annotations.analyze([out/'preferences.csv'],[out/'candidate_ratings.csv'],allow_blank=True)
        self.assertEqual(len(report['preferences']),1);self.assertEqual(len(report['ratings']),3)
        expected=sorted(r['candidate_id'] for r in crosswalk if (r['family_id'],r['audience'],r['phrasing'])==(row['family_id'],row['audience'],row['phrasing']) and r['display_id'] in ('X1','X3'))
        self.assertEqual(report['preferences'][0]['tied_candidate_ids'],'|'.join(expected))
        self.assertTrue((out/'conversion_manifest.json').exists())
        with self.assertRaises(FileExistsError):unblind.convert(pref,rating,mapping_path,out)
    def test_wrong_crosswalk_or_modified_text_rejected(self):
        pref=self.b/'reviewer_1_preferences.csv';rating=self.b/'reviewer_1_candidate_ratings.csv';crosswalk=self.m/'reviewer_2_crosswalk.csv'
        with self.assertRaises(ValueError):unblind.convert(pref,rating,crosswalk,self.base/'out')
        fields,rows=self.read(rating);rows[0]['candidate_text']='changed';self.write(rating,fields,rows)
        with self.assertRaisesRegex(ValueError,'differs'):unblind.convert(pref,rating,self.m/'reviewer_1_crosswalk.csv',self.base/'out')
    def test_direct_import_keeps_original_provenance(self):
        pref=self.b/'reviewer_1_preferences.csv';rating=self.b/'reviewer_1_candidate_ratings.csv';mapping=self.m/'reviewer_1_crosswalk.csv'
        fields,rows=self.read(pref);rows[0].update(preferred_candidate_id='X1',decision_rationale='synthetic',annotator_id='fixture');self.write(pref,fields,rows)
        report=self.base/'report.json'
        proc=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/annotations.py'),'--allow-blank','--preferences',str(pref),'--ratings',str(rating),'--blinded-crosswalk',str(mapping),'--output',str(report)],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        data=json.loads(report.read_text());self.assertEqual(data['preferences'][0]['source_path'],str(pref.resolve()))
        self.assertEqual(data['sources'][0]['sha256'],unblind.digest(pref))
        self.assertEqual(data['crosswalk']['sha256'],unblind.digest(mapping))
    def test_blinded_rows_do_not_expose_original_ids_or_register_labels(self):
        _,rows=self.read(self.b/'reviewer_1_candidate_ratings.csv')
        self.assertEqual({r['candidate_id'] for r in rows},{'X1','X2','X3'})
        self.assertNotIn('register_label',rows[0])

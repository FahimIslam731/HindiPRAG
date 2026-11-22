import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import annotations
import annotation_coverage as coverage
import prepare_annotation_packets as packets

class PacketTests(unittest.TestCase):
    def test_assignments_randomization_and_source_integrity(self):
        records = [json.loads(x) for x in packets.SOURCE.read_text().splitlines()]
        splits = json.loads(packets.SPLITS.read_text())['splits']
        first=packets.build_packets(records,splits); self.assertEqual(first,packets.build_packets(records,splits))
        self.assertEqual([len(first[x][0]) for x in ('reviewer_1','reviewer_2')],[800,416])
        self.assertEqual([len(first[x][1]) for x in ('reviewer_1','reviewer_2')],[2400,1248])
        reviewer2={row['family_id'] for row in first['reviewer_2'][0]}
        self.assertEqual(reviewer2, set(splits['validation'])|set(splits['test'])|{f'F{i:03}' for i in range(1,25)})
        source={r['family_id']:r for r in records}; orders=set()
        for _, ratings in first.values():
            for i in range(0,len(ratings),3):
                triplet=ratings[i:i+3]; orders.add(''.join(row['candidate_id'] for row in triplet))
                self.assertEqual({row['candidate_id'] for row in triplet},{'A','B','C'})
                for row in triplet:
                    candidate=next(c for c in source[row['family_id']]['candidates'] if c['id']==row['candidate_id'])
                    self.assertEqual(row['candidate_text'], candidate['text'])
        self.assertGreater(len(orders),1)
        self.assertNotIn('register_label',packets.RATING_FIELDS)
    def test_blank_and_partially_completed_packets_import(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'packets'; packets.write_packets(out)
            pref=out/'reviewer_1_preferences.csv'; rating=out/'reviewer_1_candidate_ratings.csv'
            blank=coverage.coverage([pref],[rating]); self.assertEqual(blank['total']['missing_judgments'],1216)
            with pref.open(newline='',encoding='utf-8') as h:
                reader=csv.DictReader(h); fields=reader.fieldnames; rows=list(reader)
            rows[0].update(preferred_candidate_id='A',decision_rationale='synthetic fixture',annotator_id='fixture')
            with pref.open('w',newline='',encoding='utf-8') as h:
                writer=csv.DictWriter(h,fieldnames=fields);writer.writeheader();writer.writerows(rows)
            result=coverage.coverage([pref],[rating]); self.assertEqual(result['total']['total_valid_preference_records'],1)
            self.assertEqual(result['total']['missing_judgments'],1215)
            self.assertEqual(len(annotations.analyze([pref],[rating],allow_blank=True)['preferences']),1)
            rows[1]['preferred_candidate_id']='B'
            with pref.open('w',newline='',encoding='utf-8') as h:
                writer=csv.DictWriter(h,fieldnames=fields);writer.writeheader();writer.writerows(rows)
            with self.assertRaisesRegex(ValueError,'annotator_id'): coverage.coverage([pref],[rating])
    def test_packet_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'packets'; packets.write_packets(out)
            with self.assertRaises(FileExistsError): packets.write_packets(out)

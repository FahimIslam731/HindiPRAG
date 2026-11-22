import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('annotations', ROOT / 'scripts/annotations.py')
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)

class AnnotationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'votes.csv'
        with (ROOT / 'pilot/preferences_template.csv').open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f); self.fields = reader.fieldnames; self.row = next(reader)
    def tearDown(self): self.tmp.cleanup()
    def write(self, rows):
        with self.path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=self.fields); w.writeheader(); w.writerows(rows)
    def vote(self, who, choice, tie=''):
        return dict(self.row, annotator_id=who, preferred_candidate_id=choice, tied_candidate_ids=tie, decision_rationale='fixture')
    def test_realistic_independent_records_and_agreement(self):
        self.write([self.vote('one', 'A'), self.vote('two', 'tie', 'A|C')])
        out = a.analyze([self.path]); self.assertEqual(out['coverage']['prompts_with_two_or_more'], 1)
        self.assertEqual(out['agreement'][0]['exact_agreement'], 0)
        self.assertEqual(out['preferences'][1]['tied_candidate_ids'], 'A|C')
    def test_reject_duplicate_reviewer(self):
        self.write([self.vote('one', 'A'), self.vote('one', 'B')])
        with self.assertRaisesRegex(ValueError, 'duplicate'): a.analyze([self.path])
    def test_reject_invalid_tie_and_blank_template(self):
        self.write([self.vote('one', 'tie', 'A')])
        with self.assertRaisesRegex(ValueError, 'tie requires'): a.analyze([self.path])
        self.write([self.row])
        with self.assertRaisesRegex(ValueError, 'annotator_id'): a.analyze([self.path])
    def test_detect_tampered_source_text(self):
        self.write([dict(self.vote('one', 'A'), prompt_text='changed')])
        with self.assertRaisesRegex(ValueError, 'differs'): a.analyze([self.path])
    def test_adjudication_requires_linked_originals(self):
        self.write([self.vote('one', 'A'), self.vote('two', 'B')])
        adjudication = Path(self.tmp.name) / 'adjudication.csv'
        fields = self.fields + ['source_reviewers']
        with adjudication.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            w.writerow(dict(self.vote('third', 'tie', 'A|B'), source_reviewers='one|two'))
        out = a.analyze([self.path], adjudication_paths=[adjudication])
        self.assertEqual(len(out['adjudications']), 1)
        with self.assertRaisesRegex(ValueError, 'source_reviewers'):
            a.analyze([], adjudication_paths=[adjudication])
    def test_rating_coverage_is_per_reviewer_and_prompt(self):
        path = Path(self.tmp.name) / 'ratings.csv'
        with (ROOT / 'pilot/candidate_ratings_template.csv').open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f); fields = reader.fieldnames; rows = [next(reader) for _ in range(3)]
        for row in rows:
            row.update(annotator_id='r1', meaning_fidelity='pass', register_fit='appropriate', naturalness_1_to_5='4')
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        out = a.analyze([], [path]); self.assertEqual(out['coverage']['rating_reviewer_prompts_complete'], 1)
    def test_empty_coverage_does_not_invent_labels(self):
        out = a.analyze([]); self.assertEqual(out['coverage']['prompts'], 800)
        self.assertEqual(out['coverage']['preference_records'], 0)
        self.assertEqual(out['agreement'], [])

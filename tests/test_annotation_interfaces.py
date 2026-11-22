"""Synthetic UI data/handler tests. These do not claim interactive browser testing."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import annotation_coverage
import annotations
import blind_annotation_packets
import build_annotation_interfaces
import prepare_annotation_packets
import unblind_annotation_packet


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.packets, self.blind, self.maps = (self.base / name for name in ('packets', 'blind', 'maps'))
        prepare_annotation_packets.write_packets(self.packets)
        blind_annotation_packets.generate(self.blind, self.maps, self.packets)
        self.ui = build_annotation_interfaces.build(self.blind, self.base / 'ui')

    def test_full_export_restore_merge_import_and_coordinator_counts(self):
        subprocess.run(['node', str(ROOT / 'tests/annotation_interface_checks.js'),
                        str(self.ui), str(self.base)], check=True)
        converted = []
        for n, expected in ((1, 800), (2, 416)):
            output = self.base / f'converted{n}'
            unblind_annotation_packet.convert(self.base / f'r{n}-preferences.csv',
                                             self.base / f'r{n}-ratings.csv',
                                             self.maps / f'reviewer_{n}_crosswalk.csv', output)
            pref, ratings = output / 'preferences.csv', output / 'candidate_ratings.csv'
            report = annotations.analyze([pref], [ratings], allow_blank=True)
            self.assertEqual(report['coverage']['preference_records'], expected)
            self.assertEqual(report['coverage']['rating_records'], expected * 3)
            converted.append((pref, ratings))
        coverage = annotation_coverage.coverage([p for p, _ in converted], [r for _, r in converted])
        self.assertEqual(coverage['total']['required_judgments'], 1216)
        self.assertEqual(coverage['total']['missing_judgments'], 0)
        self.assertEqual(coverage['total']['candidate_rating_records'], 3648)

    def test_distribution_has_no_crosswalks_or_stable_ids(self):
        for n in (1, 2):
            folder = self.ui / f'reviewer{n}'
            self.assertEqual({p.name for p in folder.iterdir()},
                             {'index.html', 'core.js', 'interface.js', 'packet.js'})
            text = (folder / 'packet.js').read_text()
            packet = json.loads(text.removeprefix('window.PACKET=').strip().removesuffix(';'))
            self.assertEqual({r['candidate_id'] for r in packet['ratings']}, {'X1', 'X2', 'X3'})
            self.assertNotIn('register_label', text)
            self.assertTrue(all(not r['annotator_id'] for r in packet['preferences']))

    def test_builder_refuses_overwrite_or_public_output(self):
        with self.assertRaises(FileExistsError):
            build_annotation_interfaces.build(self.blind, self.ui)
        with self.assertRaises(ValueError):
            build_annotation_interfaces.build(self.blind, ROOT / 'unsafe-output')

    def test_builder_refuses_answered_packets(self):
        path = self.blind / 'reviewer_1_preferences.csv'
        fields, rows = blind_annotation_packets.read(path)
        rows[0]['annotator_id'] = 'synthetic-do-not-distribute'
        path.unlink()
        blind_annotation_packets.write(path, fields, rows)
        output = self.base / 'answered-ui'
        with self.assertRaisesRegex(ValueError, 'Only blank packets'):
            build_annotation_interfaces.build(self.blind, output)
        self.assertFalse(output.exists())

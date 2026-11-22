import csv
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("scripts", "data", "pilot", "docs"):
            shutil.copytree(ROOT / name, self.root / name)
        for name in ("README.md", "validation_report.md", "families.json"):
            shutil.copy2(ROOT / name, self.root / name)

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        return subprocess.run([sys.executable, "-B", "scripts/validate_release.py"],
                              cwd=self.root, text=True, capture_output=True)

    def test_existing_release_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_root_json_drift_fails(self):
        path = self.root / "families.json"
        data = json.loads(path.read_text())
        data[0]["intent"] = "changed"
        path.write_text(json.dumps(data))
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Root and draft JSON records differ", result.stdout)

    def test_template_source_text_drift_fails(self):
        path = self.root / "pilot/preferences_template.csv"
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields, rows = reader.fieldnames, list(reader)
        rows[0]["prompt_text"] = "changed"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("template prompt_text differs", result.stdout)

    def test_malformed_issue_csv_fails_cleanly(self):
        path = self.root / "pilot/issues_log.csv"
        path.write_text("<PARSED TEXT FOR SHEET: broken\nnot a marker\n", encoding="utf-8")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed spreadsheet export marker", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

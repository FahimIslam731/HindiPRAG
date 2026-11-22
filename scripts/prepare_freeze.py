#!/usr/bin/env python3
"""Prepare an unfrozen Stage 2 inventory and report release blockers.

No eligibility or pairwise preference is inferred from a style tag or a
best-of-three answer. This command does not declare a dataset frozen.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    data = ROOT / 'data/draft/families.jsonl'
    splits = ROOT / 'data/splits.json'
    subset = ROOT / 'data/generation_subset.json'
    records = [json.loads(line) for line in data.read_text(encoding='utf-8').splitlines() if line.strip()]
    manifest = json.loads(splits.read_text())
    if sha(data) != manifest['dataset_sha256']:
        raise ValueError('split manifest does not match source dataset')
    mapping = {fid: name for name, ids in manifest['splits'].items() for fid in ids}
    if len(mapping) != len(records) or set(mapping) != {r['family_id'] for r in records}:
        raise ValueError('split manifest does not cover dataset exactly')
    processed = output / 'families.jsonl'
    eligibility = output / 'eligibility.jsonl'
    with processed.open('w', encoding='utf-8') as dst, eligibility.open('w', encoding='utf-8') as flags:
        for r in records:
            dst.write(json.dumps({'family': r, 'split': mapping[r['family_id']]}, ensure_ascii=False) + '\n')
            flags.write(json.dumps({'family_id': r['family_id'], 'jra_eligible': None, 'sc_eligible': None,
                                   'reason': 'preference evidence and pairwise eligibility policy not yet established'}) + '\n')
    result = {'status': 'BLOCKED', 'dataset_version': None,
              'blockers': ['genuine independent preference annotations and adjudications not supplied', 'pairwise mapping and eligibility policy not specified'],
              'denominators': {'families': len(records), 'jra': None, 'sc': None},
              'inputs': {str(p.relative_to(ROOT)): sha(p) for p in [data, splits, subset]},
              'outputs': {p.name: sha(p) for p in [processed, eligibility]}}
    (output / 'manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', required=True)
    args = p.parse_args(); result = prepare(args.output)
    print(json.dumps(result, indent=2))
    return 2

if __name__ == '__main__': raise SystemExit(main())

#!/usr/bin/env python3
"""Create a versioned release only from explicitly supplied pairwise judgments.

This tool does not convert three-way winners into pairwise preferences. The
protocol owner must supply a documented candidate pair for every family and
actual pairwise reviewer records, including adjudication where reviewers differ.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import create_splits

CONTEXTS = [(a, p) for a in ('familiar', 'respectful') for p in ('scenario', 'paraphrase')]
OUTCOMES = {'left', 'right', 'tie', 'unclear', 'none'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        required = {'family_id', 'audience', 'phrasing', 'left_id', 'right_id', 'outcome', 'annotator_id', 'rationale'}
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames) or not required <= set(reader.fieldnames):
            raise ValueError(f'{path}: missing or duplicate CSV columns')
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f'{path}: malformed CSV row')
    return rows


def evaluate(policy_path, judgment_paths, adjudication_paths=(), dataset_path=None, split_path=None, subset_path=None):
    dataset_path = Path(dataset_path or ROOT / 'data/draft/families.jsonl')
    split_path = Path(split_path or ROOT / 'data/splits.json')
    subset_path = Path(subset_path or ROOT / 'data/generation_subset.json')
    policy_path = Path(policy_path)
    policy = json.loads(policy_path.read_text(encoding='utf-8'))
    for key in ('version', 'approved_by', 'approval_evidence', 'pairwise_instructions', 'independence_evidence'):
        if not isinstance(policy.get(key), str) or not policy[key].strip():
            raise ValueError(f'policy requires nonempty {key}')
    records = [json.loads(x) for x in dataset_path.read_text(encoding='utf-8').splitlines() if x.strip()]
    ids = [r['family_id'] for r in records]
    if len(ids) != 200 or len(set(ids)) != 200:
        raise ValueError('dataset must contain 200 unique families')
    pairs = policy.get('pairs')
    if not isinstance(pairs, dict) or set(pairs) != set(ids):
        raise ValueError('policy requires an explicit pair for every family')
    for fid, pair in pairs.items():
        if not isinstance(pair, list) or len(pair) != 2 or len(set(pair)) != 2 or not set(pair) <= {'A', 'B', 'C'}:
            raise ValueError(f'{fid}: invalid explicit candidate pair')
    split_manifest = json.loads(split_path.read_text(encoding='utf-8'))
    if sha(dataset_path) != split_manifest['dataset_sha256']:
        raise ValueError('split manifest dataset hash mismatch')
    allocations = split_manifest['splits']
    if set(allocations) != {'train', 'validation', 'test'}:
        raise ValueError('invalid split names')
    flat = [fid for bucket in allocations.values() for fid in bucket]
    if len(flat) != len(ids) or len(set(flat)) != len(ids) or set(flat) != set(ids):
        raise ValueError('split assignment missing, duplicated or unknown family')
    lookup = {fid: group for group, members in allocations.items() for fid in members}
    if not {f'F{i:03d}' for i in range(1,25)} <= set(allocations['train']):
        raise ValueError('pilot families must remain in training')
    by_group = defaultdict(set)
    for rec in records: by_group[rec['template_group_id']].add(lookup[rec['family_id']])
    if any(len(groups) != 1 for groups in by_group.values()):
        raise ValueError('template group leakage')
    for left, right in create_splits.LINKS:
        if lookup[left] != lookup[right]: raise ValueError('conservative overlap link leakage')
    subset = json.loads(subset_path.read_text(encoding='utf-8'))['family_ids']
    if len(subset) != 30 or len(set(subset)) != 30 or not set(subset) <= set(allocations['test']):
        raise ValueError('generation subset must contain 30 unique test families')
    votes, adjudications = defaultdict(dict), {}
    sources = []
    for kind, paths in [('judgment', judgment_paths), ('adjudication', adjudication_paths)]:
        for path in paths:
            path = Path(path)
            sources.append({'kind': kind, 'path': str(path.resolve()), 'sha256': sha(path)})
            for line, row in enumerate(read_csv(path), 2):
                fid, a, p = (row[k] for k in ('family_id', 'audience', 'phrasing'))
                key = (fid, a, p)
                if fid not in pairs or (a, p) not in CONTEXTS or [row['left_id'], row['right_id']] != pairs[fid]:
                    raise ValueError(f'{path}:{line}: unknown context or inconsistent ordered candidate pair')
                reviewer, outcome = row['annotator_id'].strip(), row['outcome']
                if not reviewer or outcome not in OUTCOMES or not row['rationale'].strip():
                    raise ValueError(f'{path}:{line}: reviewer, outcome and rationale required')
                row = dict(row, source_path=str(path.resolve()), source_row=line)
                if kind == 'judgment':
                    if reviewer in votes[key]: raise ValueError(f'{path}:{line}: duplicate reviewer')
                    votes[key][reviewer] = row
                else:
                    if key in adjudications: raise ValueError(f'{path}:{line}: duplicate adjudication')
                    adjudications[key] = row
    for key, decision in adjudications.items():
        reviewers = decision.get('source_reviewers', '').split('|')
        if len(reviewers) < 2 or len(set(reviewers)) != len(reviewers) or not set(reviewers) <= set(votes[key]) or decision['annotator_id'] in reviewers:
            raise ValueError(f'{decision["source_path"]}:{decision["source_row"]}: invalid adjudication source reviewers')
    flags, missing, unresolved = [], [], []
    pilot = {f'F{i:03d}' for i in range(1,25)}
    for fid in ids:
        resolved = {}
        for audience, phrasing in CONTEXTS:
            key = (fid, audience, phrasing)
            raw = votes.get(key, {})
            minimum = 2 if lookup[fid] != 'train' or fid in pilot else 1
            if len(raw) < minimum:
                missing.append({'family_id': fid, 'audience': audience, 'phrasing': phrasing, 'required': minimum, 'present': len(raw)})
                resolved[(audience, phrasing)] = None
                continue
            outcomes = {row['outcome'] for row in raw.values()}
            if len(outcomes) == 1:
                resolved[(audience, phrasing)] = next(iter(outcomes))
            elif key in adjudications:
                resolved[(audience, phrasing)] = adjudications[key]['outcome']
            else:
                unresolved.append({'family_id': fid, 'audience': audience, 'phrasing': phrasing})
                resolved[(audience, phrasing)] = None
        f, r = resolved[('familiar','scenario')], resolved[('respectful','scenario')]
        fp, rp = resolved[('familiar','paraphrase')], resolved[('respectful','paraphrase')]
        # These are the proposal's fixed-pair strict reversal and paraphrase rules.
        jra = f == 'left' and r == 'right'
        sc = jra and fp == 'left' and rp == 'right'
        reason_jra = [] if jra else ['missing_or_unresolved' if f is None or r is None else 'originals_not_strict_reversal']
        reason_sc = [] if sc else (reason_jra or ['missing_or_unresolved_paraphrase' if fp is None or rp is None else 'paraphrases_not_matching_reversal'])
        flags.append({'family_id': fid, 'split': lookup[fid], 'left_id': pairs[fid][0], 'right_id': pairs[fid][1],
                      'resolved': {f'{a}.{p}': resolved[(a,p)] for a,p in CONTEXTS},
                      'jra_eligible': jra, 'sc_eligible': sc, 'jra_exclusion_reasons': reason_jra, 'sc_exclusion_reasons': reason_sc})
    denominators = {bucket: {'families': len(members), 'jra': sum(r['jra_eligible'] for r in flags if r['split'] == bucket), 'sc': sum(r['sc_eligible'] for r in flags if r['split'] == bucket)} for bucket, members in allocations.items()}
    return {'records': records, 'flags': flags, 'votes': votes, 'adjudications': adjudications, 'sources': sources,
            'missing': missing, 'unresolved': unresolved, 'denominators': denominators, 'policy': policy,
            'inputs': {'dataset': sha(dataset_path), 'splits': sha(split_path), 'generation_subset': sha(subset_path), 'policy': sha(policy_path)}}


def release(output, version, policy_path, judgments, adjudications=()):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', version): raise ValueError('invalid dataset version')
    result = evaluate(policy_path, judgments, adjudications)
    if result['missing'] or result['unresolved']:
        return {'status': 'BLOCKED', 'missing_contexts': result['missing'], 'unresolved_contexts': result['unresolved'], 'denominators': result['denominators']}
    check = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/validate_release.py')], cwd=ROOT, capture_output=True, text=True)
    if check.returncode:
        raise ValueError('draft validation failed: ' + check.stdout + check.stderr)
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    def write_json(name, value):
        (output/name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (output/'families.jsonl').open('w', encoding='utf-8') as f:
        flag_map = {r['family_id']:r for r in result['flags']}
        for rec in result['records']:
            flag = flag_map[rec['family_id']]
            f.write(json.dumps({'family': rec, 'split': flag['split']}, ensure_ascii=False) + '\n')
    with (output/'eligibility.jsonl').open('w', encoding='utf-8') as f:
        for row in result['flags']: f.write(json.dumps(row, ensure_ascii=False) + '\n')
    write_json('judgments.json', [r for group in result['votes'].values() for r in group.values()])
    write_json('adjudications.json', list(result['adjudications'].values()))
    write_json('pairwise_policy.json', result['policy'])
    for name, path in [('splits.json', ROOT/'data/splits.json'), ('generation_subset.json', ROOT/'data/generation_subset.json')]:
        (output/name).write_bytes(path.read_bytes())
    exclusions = {split: {'jra': dict(Counter(reason for f in result['flags'] if f['split'] == split for reason in f['jra_exclusion_reasons'])), 'sc': dict(Counter(reason for f in result['flags'] if f['split'] == split for reason in f['sc_exclusion_reasons']))} for split in result['denominators']}
    files = {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()}
    manifest = {'status': 'FROZEN', 'dataset_version': version, 'input_sha256': result['inputs'], 'annotation_sources': result['sources'],
                'denominators': result['denominators'], 'exclusion_counts': exclusions, 'files_sha256': files,
                'limitations': ['Reviewer independence and protocol approval are attestations requiring human verification.', 'Pairwise labels must be genuine; the tool cannot verify human provenance.']}
    write_json('manifest.json', manifest)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', required=True); p.add_argument('--policy', required=True)
    p.add_argument('--judgments', action='append', required=True); p.add_argument('--adjudications', action='append', default=[])
    p.add_argument('--output', required=True)
    args = p.parse_args()
    try:
        result = release(args.output, args.version, args.policy, args.judgments, args.adjudications)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f'ERROR: {exc}\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'FROZEN' else 2

if __name__ == '__main__': sys.exit(main())

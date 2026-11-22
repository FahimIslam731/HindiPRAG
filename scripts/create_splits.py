#!/usr/bin/env python3
"""Generate deterministic family splits, conservatively linking flagged overlaps."""
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/draft/families.jsonl'
# Conservative leakage links from the M0 lexical screen; not semantic decisions.
LINKS = [('F006','F049'), ('F041','F070'), ('F139','F157'), ('F153','F184')]
SEED = 731

def build(records):
    ids = {r['family_id'] for r in records}
    if len(ids) != len(records) or len(ids) != 200:
        raise ValueError('expected 200 unique families')
    parent = {fid: fid for fid in ids}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b: parent[max(a,b)] = min(a,b)
    groups = defaultdict(list)
    for rec in records: groups[rec['template_group_id']].append(rec['family_id'])
    for members in groups.values():
        for fid in members[1:]: union(members[0], fid)
    for a, b in LINKS: union(a, b)
    linked = defaultdict(list)
    for fid in sorted(ids): linked[find(fid)].append(fid)
    components = sorted(linked.values())
    pilot = {f'F{i:03}' for i in range(1,25)}
    forced = [g for g in components if pilot.intersection(g)]
    remaining = [g for g in components if not pilot.intersection(g)]
    rng = random.Random(SEED); rng.shuffle(remaining)
    # Place larger components first; singleton groups make exact quotas possible here.
    remaining.sort(key=len, reverse=True)
    splits = {'train': sorted(x for g in forced for x in g), 'validation': [], 'test': []}
    targets = {'train': 120, 'validation': 30, 'test': 50}
    for group in remaining:
        eligible = [k for k in splits if len(splits[k]) + len(group) <= targets[k]]
        if not eligible: raise ValueError('cannot meet targets without splitting a group')
        bucket = max(eligible, key=lambda k: targets[k] - len(splits[k]))
        splits[bucket].extend(group)
    for values in splits.values(): values.sort()
    if {k:len(v) for k,v in splits.items()} != targets: raise ValueError('target counts unavailable')
    test = splits['test'].copy(); random.Random(SEED + 1).shuffle(test)
    return {'seed': SEED, 'dataset_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest(),
            'targets': targets, 'conservative_links': LINKS, 'splits': splits}, {'seed': SEED + 1, 'selection': 'random sample from test families before model output inspection', 'family_ids': sorted(test[:30])}

def main():
    records = [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]
    splits, subset = build(records)
    for filename, obj in [('splits.json', splits), ('generation_subset.json', subset)]:
        path = ROOT / 'data' / filename
        with path.open('x', encoding='utf-8') as f: json.dump(obj, f, indent=2); f.write('\n')
        print(f'Created {path}')

if __name__ == '__main__': main()

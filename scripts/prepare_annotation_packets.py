#!/usr/bin/env python3
"""Create blank, randomized, import-compatible Stage 2 annotation packets."""
import csv
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/draft/families.jsonl'
SPLITS = ROOT / 'data/splits.json'
OUT = ROOT.parent / 'HindiPRAG-private/packets'
PREF_FIELDS = ['family_id','template_group_id','topic','audience','relationship','phrasing','prompt_text','preferred_candidate_id','tied_candidate_ids','decision_rationale','annotator_id','annotated_at','adjudication_status']
# Hide style tags so they do not bias review. Candidate IDs remain stable.
RATING_FIELDS = ['family_id','template_group_id','topic','audience','relationship','phrasing','prompt_text','candidate_id','candidate_text','meaning_fidelity','register_fit','naturalness_1_to_5','error_tags','rationale','annotator_id','annotated_at']


def build_packets(records, splits):
    by_id = {r['family_id']:r for r in records}
    flat = [x for group in splits.values() for x in group]
    if len(flat) != len(set(flat)) or set(flat) != set(by_id): raise ValueError('invalid split coverage')
    pilot = {f'F{i:03}' for i in range(1,25)}
    assignments = {'reviewer_1': set(flat), 'reviewer_2': pilot | set(splits['validation']) | set(splits['test'])}
    result = {}
    for i, (reviewer, assigned) in enumerate(assignments.items(), 1):
        rng = random.Random(261121 + i)
        prompts = [(fid, a, p) for fid in sorted(assigned) for a in ('familiar','respectful') for p in ('scenario','paraphrase')]
        rng.shuffle(prompts); preferences=[]; ratings=[]
        for fid, audience, phrasing in prompts:
            family = by_id[fid]; context = family['contexts'][audience]
            common = {'family_id':fid,'template_group_id':family['template_group_id'],'topic':family['topic'], 'audience':audience, 'relationship':context['relationship'], 'phrasing':phrasing, 'prompt_text':context[phrasing]}
            preferences.append(common.copy())
            candidates = list(family['candidates']); rng.shuffle(candidates)
            for candidate in candidates:
                ratings.append(dict(common, candidate_id=candidate['id'], candidate_text=candidate['text']))
        result[reviewer] = (preferences, ratings)
    return result


def write_packets(output=OUT):
    records = [json.loads(x) for x in SOURCE.read_text(encoding='utf-8').splitlines() if x.strip()]
    manifest = json.loads(SPLITS.read_text(encoding='utf-8'))
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != manifest['dataset_sha256']: raise ValueError('dataset does not match split manifest')
    packets = build_packets(records, manifest['splits'])
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    for reviewer, (preferences, ratings) in packets.items():
        for suffix, fields, rows in [('preferences', PREF_FIELDS, preferences), ('candidate_ratings', RATING_FIELDS, ratings)]:
            with (output/f'{reviewer}_{suffix}.csv').open('x', encoding='utf-8', newline='') as h:
                writer = csv.DictWriter(h, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    return packets

if __name__ == '__main__':
    packets=write_packets()
    for name, (p, r) in packets.items(): print(f'{name}: {len(p)} prompt decisions, {len(r)} candidate ratings')

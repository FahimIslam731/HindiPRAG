#!/usr/bin/env python3
"""Report coverage from actual, validated annotation CSVs; blank rows are ignored."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
import annotations

ROOT = Path(__file__).resolve().parents[1]


def coverage(pref_paths, rating_paths=(), adjudications=()):
    report = annotations.analyze(pref_paths, rating_paths, adjudications, allow_blank=True)
    splits = json.loads((ROOT/'data/splits.json').read_text())['splits']
    allocations = {fid: bucket for bucket, ids in splits.items() for fid in ids}
    pilot = {f'F{i:03d}' for i in range(1,25)}
    votes = defaultdict(dict)
    for row in report['preferences']:
        key = (row['family_id'], row['audience'], row['phrasing'])
        votes[key][row['annotator_id']] = (row['preferred_candidate_id'], row.get('tied_candidate_ids',''))
    adjudicated = {(r['family_id'], r['audience'], r['phrasing']) for r in report['adjudications']}
    by_split = {}; disagreements = []; unmatched = []
    for split, families in splits.items():
        required = valid = missing = prompts_complete = 0
        for fid in families:
            for audience in annotations.AUDIENCES:
                for phrasing in annotations.PHRASINGS:
                    key = (fid,audience,phrasing); results = votes.get(key,{})
                    need = 2 if split != 'train' or fid in pilot else 1
                    required += need; valid += min(need,len(results)); missing += max(0,need-len(results))
                    prompts_complete += len(results) >= need
                    if len(set(results.values())) > 1 and key not in adjudicated: disagreements.append(list(key))
                    if len(results) < need: unmatched.append({'family_id':fid,'audience':audience,'phrasing':phrasing,'missing':need-len(results)})
        by_split[split]={'prompt_contexts':len(families)*4,'required_judgments':required,'present_toward_minimum':valid,'missing_judgments':missing,'contexts_with_required_count':prompts_complete}
    return {'by_split':by_split, 'total':{'required_judgments':sum(v['required_judgments'] for v in by_split.values()), 'present_toward_minimum':sum(v['present_toward_minimum'] for v in by_split.values()), 'missing_judgments':sum(v['missing_judgments'] for v in by_split.values()), 'total_valid_preference_records':len(report['preferences']), 'candidate_rating_records':len(report['ratings']), 'adjudication_records':len(report['adjudications']), 'disagreements_requiring_adjudication':len(disagreements)}, 'independence_evidence':'Not verified by tool; distinct IDs do not establish independent blinded review.', 'pairwise_evidence':'Not assessed: three-way choices do not resolve all pairwise comparisons.', 'missing_contexts':unmatched, 'unadjudicated_disagreements':disagreements,'sources':report['sources']}


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--preferences',action='append',default=[]); p.add_argument('--ratings',action='append',default=[]); p.add_argument('--adjudications',action='append',default=[]); p.add_argument('--output',required=True)
    a=p.parse_args()
    try:
        result=coverage(a.preferences,a.ratings,a.adjudications)
        with Path(a.output).open('x',encoding='utf-8') as h: json.dump(result,h,ensure_ascii=False,indent=2); h.write('\n')
    except (ValueError,KeyError,OSError) as exc: p.exit(1,f'ERROR: {exc}\n')
    print(json.dumps({'by_split':result['by_split'], 'total':result['total'], 'independence_evidence':result['independence_evidence']},indent=2))

if __name__ == '__main__': main()

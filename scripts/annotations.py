#!/usr/bin/env python3
"""Validate real annotation CSVs and summarize independent prompt judgments.

Outputs reference original files and hashes; input files are never modified.
"""
import argparse
import csv
import hashlib
import itertools
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIENCES = ('familiar', 'respectful')
PHRASINGS = ('scenario', 'paraphrase')
CHOICES = {'A', 'B', 'C', 'tie', 'none', 'unclear'}


def load_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError(f'{path}: invalid header')
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f'{path}: malformed row')
    return rows


def analyze(preference_paths, rating_paths=(), adjudication_paths=(), allow_blank=False):
    families = {r['family_id']: r for r in json.loads((ROOT / 'data/draft/families.json').read_text())}
    records, ratings, adjudications, sources = [], [], [], []
    seen = set()
    for kind, paths in [('preference', preference_paths), ('rating', rating_paths), ('adjudication', adjudication_paths)]:
        for path in paths:
            path = Path(path)
            sources.append({'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'kind': kind})
            for lineno, row in enumerate(load_csv(path), 2):
                answer_fields = (('preferred_candidate_id', 'tied_candidate_ids', 'decision_rationale', 'annotator_id', 'annotated_at', 'adjudication_status') if kind != 'rating' else ('meaning_fidelity', 'register_fit', 'naturalness_1_to_5', 'error_tags', 'rationale', 'annotator_id', 'annotated_at'))
                if allow_blank and all(not row.get(field, '').strip() for field in answer_fields):
                    continue
                def fail(message):
                    raise ValueError(f'{path}:{lineno}: {message}')
                fid, audience, phrasing = (row.get(k, '') for k in ('family_id', 'audience', 'phrasing'))
                if fid not in families or audience not in AUDIENCES or phrasing not in PHRASINGS:
                    fail('invalid family, audience or phrasing')
                family = families[fid]
                context = family['contexts'][audience]
                for field, expected in [('template_group_id', family['template_group_id']), ('topic', family['topic']), ('relationship', context['relationship']), ('prompt_text', context[phrasing])]:
                    if field in row and row[field] != expected:
                        fail(f'{field} differs from dataset')
                person = row.get('annotator_id', '').strip()
                if not person:
                    fail('annotator_id is required for real records')
                key = (fid, audience, phrasing, person, kind, row.get('candidate_id', ''))
                if key in seen:
                    fail('duplicate reviewer record')
                seen.add(key)
                enriched = dict(row, source_path=str(path.resolve()), source_row=lineno)
                if kind in ('preference', 'adjudication'):
                    choice = row.get('preferred_candidate_id', '')
                    if choice not in CHOICES:
                        fail('invalid or missing preference')
                    tied = row.get('tied_candidate_ids', '')
                    if choice == 'tie':
                        parts = tied.split('|')
                        if len(parts) < 2 or parts != sorted(set(parts)) or not set(parts) <= {'A', 'B', 'C'}:
                            fail('tie requires two or three distinct sorted candidate IDs')
                    elif tied:
                        fail('tied IDs require tie decision')
                    if not row.get('decision_rationale', '').strip():
                        fail('decision rationale is required')
                    (records if kind == 'preference' else adjudications).append(enriched)
                else:
                    cid = row.get('candidate_id', '')
                    candidate = next((c for c in family['candidates'] if c['id'] == cid), None)
                    if candidate is None:
                        fail('invalid candidate')
                    for field, expected in [('candidate_text', candidate['text']), ('register_label', candidate['register_label'])]:
                        if field in row and row[field] != expected:
                            fail(f'{field} differs from dataset')
                    if row.get('meaning_fidelity') not in {'pass', 'minor_issue', 'major_issue', 'unclear'} or row.get('register_fit') not in {'appropriate', 'borderline', 'inappropriate', 'unclear'} or row.get('naturalness_1_to_5') not in {'1','2','3','4','5'}:
                        fail('invalid candidate rating')
                    ratings.append(enriched)
    prompt_votes = defaultdict(dict)
    for row in records:
        key = tuple(row[k] for k in ('family_id', 'audience', 'phrasing'))
        prompt_votes[key][row['annotator_id']] = (row['preferred_candidate_id'], row.get('tied_candidate_ids', ''))
    adjudicated_keys = set()
    for row in adjudications:
        key = tuple(row[k] for k in ('family_id', 'audience', 'phrasing'))
        if key in adjudicated_keys:
            raise ValueError(f"{row['source_path']}:{row['source_row']}: duplicate adjudication for prompt")
        adjudicated_keys.add(key)
        reviewers = row.get('source_reviewers', '').split('|')
        if len(reviewers) < 2 or len(set(reviewers)) != len(reviewers) or not set(reviewers) <= set(prompt_votes[key]):
            raise ValueError(f"{row['source_path']}:{row['source_row']}: adjudication requires source_reviewers referring to at least two original judgments")
        if row['annotator_id'] in reviewers:
            raise ValueError(f"{row['source_path']}:{row['source_row']}: adjudicator must differ from source reviewers")
    pairs = defaultdict(list)
    for votes in prompt_votes.values():
        for a, b in itertools.combinations(sorted(votes), 2):
            pairs[(a, b)].append((votes[a], votes[b]))
    agreement = []
    for (a, b), votes in sorted(pairs.items()):
        n = len(votes); exact = sum(x == y for x, y in votes)
        left, right = Counter(x for x, _ in votes), Counter(y for _, y in votes)
        expected = sum(left[k] * right[k] for k in left.keys() | right.keys()) / (n*n)
        kappa = (exact/n - expected)/(1-expected) if expected != 1 else None
        agreement.append({'reviewers': [a, b], 'units': n, 'exact_agreement': exact/n, 'cohen_kappa': kappa})
    rating_coverage = defaultdict(set)
    for row in ratings:
        rating_coverage[tuple(row[k] for k in ('family_id', 'audience', 'phrasing', 'annotator_id'))].add(row['candidate_id'])
    return {'sources': sources, 'preferences': records, 'ratings': ratings, 'adjudications': adjudications,
            'coverage': {'families': len(families), 'prompts': len(families)*4, 'prompts_with_one_or_more': len(prompt_votes),
                         'prompts_with_two_or_more': sum(len(v) >= 2 for v in prompt_votes.values()), 'preference_records': len(records), 'rating_records': len(ratings), 'adjudication_records': len(adjudications), 'rating_reviewer_prompts_complete': sum(v == {'A', 'B', 'C'} for v in rating_coverage.values()), 'rating_reviewer_prompts_incomplete': sum(v != {'A', 'B', 'C'} for v in rating_coverage.values())},
            'agreement': agreement}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preferences', action='append', default=[])
    parser.add_argument('--ratings', action='append', default=[])
    parser.add_argument('--adjudications', action='append', default=[])
    parser.add_argument('--output', required=True, help='new JSON report path')
    parser.add_argument('--allow-blank', action='store_true', help='skip entirely unanswered packet rows; reject partially filled rows')
    parser.add_argument('--blinded-crosswalk', help='private crosswalk for one blinded preference/rating packet pair')
    args = parser.parse_args()
    try:
        if args.blinded_crosswalk:
            if len(args.preferences) != 1 or len(args.ratings) != 1 or args.adjudications:
                raise ValueError('blinded import requires exactly one preference file and one rating file; import adjudications separately')
            import unblind_annotation_packet
            with tempfile.TemporaryDirectory() as tmp:
                converted = Path(tmp) / 'converted'
                manifest = unblind_annotation_packet.convert(args.preferences[0], args.ratings[0], args.blinded_crosswalk, converted)
                result = analyze([converted / 'preferences.csv'], [converted / 'candidate_ratings.csv'], allow_blank=args.allow_blank)
                original = {'preference': str(Path(args.preferences[0]).resolve()), 'rating': str(Path(args.ratings[0]).resolve())}
                for source in result['sources']:
                    source['path'] = original[source['kind']]
                    source['sha256'] = manifest['input_sha256']['preferences' if source['kind'] == 'preference' else 'candidate_ratings']
                for kind, rows in [('preference', result['preferences']), ('rating', result['ratings'])]:
                    for row in rows: row['source_path'] = original[kind]
                result['crosswalk'] = {'path': str(Path(args.blinded_crosswalk).resolve()), 'sha256': manifest['input_sha256']['crosswalk']}
        else:
            result = analyze(args.preferences, args.ratings, args.adjudications, allow_blank=args.allow_blank)
        with Path(args.output).open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False); f.write('\n')
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()

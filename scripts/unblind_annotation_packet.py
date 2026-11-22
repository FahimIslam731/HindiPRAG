#!/usr/bin/env python3
"""Convert real reviewer aliases back to A/B/C without modifying source files."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as h:
        r=csv.DictReader(h)
        if not r.fieldnames or len(r.fieldnames)!=len(set(r.fieldnames)): raise ValueError(f'{path}: invalid header')
        rows=list(r)
    if any(None in row or any(v is None for v in row.values()) for row in rows): raise ValueError(f'{path}: malformed CSV row')
    return r.fieldnames,rows

def convert(preferences, ratings, crosswalk, output):
    pf,prefs=read(preferences); rf,ratings_rows=read(ratings); _,maps=read(crosswalk)
    families={r['family_id']:r for r in json.loads((ROOT/'data/draft/families.json').read_text(encoding='utf-8'))}
    mapping={}
    for row in maps:
        key=(row['family_id'],row['audience'],row['phrasing'],row['display_id'])
        if key in mapping or key[0] not in families or key[1] not in ('familiar','respectful') or key[2] not in ('scenario','paraphrase') or key[3] not in ('X1','X2','X3') or row['candidate_id'] not in ('A','B','C'):
            raise ValueError('invalid or duplicate crosswalk key')
        mapping[key]=row['candidate_id']
    by_context={}
    for (*context,alias),candidate in mapping.items(): by_context.setdefault(tuple(context),{})[alias]=candidate
    if any(set(values)!= {'X1','X2','X3'} or set(values.values())!={'A','B','C'} for values in by_context.values()): raise ValueError('crosswalk must be a per-context bijection')
    seen_pref=set();seen_rating=set()
    for row in prefs:
        key=tuple(row[k] for k in ('family_id','audience','phrasing'))
        if key not in by_context or key in seen_pref: raise ValueError('missing or duplicate preference context')
        seen_pref.add(key)
        family=families[key[0]]; ctx=family['contexts'][key[1]]
        if row['prompt_text']!=ctx[key[2]] or row['relationship']!=ctx['relationship']: raise ValueError('preference prompt differs from source')
        choice=row['preferred_candidate_id']; tied=row.get('tied_candidate_ids','')
        if choice in by_context[key]: row['preferred_candidate_id']=by_context[key][choice]
        elif choice not in ('','tie','none','unclear'): raise ValueError('invalid displayed preference')
        if tied:
            parts=tied.split('|')
            if len(parts)<2 or len(set(parts))!=len(parts) or any(x not in by_context[key] for x in parts): raise ValueError('invalid displayed tie')
            row['tied_candidate_ids']='|'.join(sorted(by_context[key][x] for x in parts))
    for row in ratings_rows:
        key=tuple(row[k] for k in ('family_id','audience','phrasing')); alias=row['candidate_id']; rk=(*key,alias)
        if rk not in mapping or rk in seen_rating: raise ValueError('missing or duplicate rating key')
        seen_rating.add(rk); family=families[key[0]]; ctx=family['contexts'][key[1]]
        candidate=next(c for c in family['candidates'] if c['id']==mapping[rk])
        if row['candidate_text']!=candidate['text'] or row['prompt_text']!=ctx[key[2]] or row['relationship']!=ctx['relationship']: raise ValueError('rating text differs from source or crosswalk')
        row['candidate_id']=mapping[rk]
    if seen_pref != set(by_context) or seen_rating != set(mapping): raise ValueError('packet does not match complete crosswalk')
    output=Path(output); output.mkdir(parents=True,exist_ok=False)
    for name,fields,rows in [('preferences.csv',pf,prefs),('candidate_ratings.csv',rf,ratings_rows)]:
        with (output/name).open('x',encoding='utf-8',newline='') as h:
            w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)
    provenance={'input_sha256':{'preferences':digest(preferences),'candidate_ratings':digest(ratings),'crosswalk':digest(crosswalk)},'output_sha256':{name:digest(output/name) for name in ('preferences.csv','candidate_ratings.csv')}}
    (output/'conversion_manifest.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    return provenance

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preferences',required=True);p.add_argument('--ratings',required=True);p.add_argument('--crosswalk',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    try: print(json.dumps(convert(a.preferences,a.ratings,a.crosswalk,a.output),indent=2))
    except (OSError,ValueError,KeyError,StopIteration) as exc: p.exit(1,f'ERROR: {exc}\n')
if __name__=='__main__': main()

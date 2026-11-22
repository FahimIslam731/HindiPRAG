#!/usr/bin/env python3
"""Create reviewer-facing packets with per-prompt aliases and private crosswalks."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT.parent/'HindiPRAG-private/packets'
BLINDED = ROOT.parent/'HindiPRAG-private/blinded'
MAPS = ROOT.parent/'HindiPRAG-private/private_maps'


def read(path):
    with path.open(encoding='utf-8',newline='') as h:
        r=csv.DictReader(h); return r.fieldnames,list(r)


def write(path, fields, rows):
    with path.open('x',encoding='utf-8',newline='') as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader();w.writerows(rows)


def generate(blinded=BLINDED, maps=MAPS, packets=PACKETS):
    blinded, maps=Path(blinded),Path(maps)
    # Refuse partial overwrites before writing anything.
    if blinded.exists() or maps.exists(): raise FileExistsError('blinded packet or crosswalk directory exists')
    prepared=[]
    for reviewer in ('reviewer_1','reviewer_2'):
        pf, prefs=read(Path(packets)/f'{reviewer}_preferences.csv')
        rf, ratings=read(Path(packets)/f'{reviewer}_candidate_ratings.csv')
        crosswalk=[]; grouped={}
        for row in ratings:
            key=tuple(row[k] for k in ('family_id','audience','phrasing'))
            grouped.setdefault(key,[]).append(row)
        for key, rows in grouped.items():
            if len(rows)!=3 or {r['candidate_id'] for r in rows}!={'A','B','C'}: raise ValueError(f'{key}: invalid candidates')
            for i,row in enumerate(rows,1):
                crosswalk.append(dict(zip(('family_id','audience','phrasing','display_id','candidate_id'),(*key,f'X{i}',row['candidate_id']))))
                row['candidate_id']=f'X{i}'
        if len(grouped)!=len(prefs): raise ValueError('prompt count mismatch')
        prepared.append((reviewer,pf,prefs,rf,ratings,crosswalk))
    blinded.mkdir(parents=True); maps.mkdir(parents=True)
    for reviewer,pf,prefs,rf,ratings,crosswalk in prepared:
        write(blinded/f'{reviewer}_preferences.csv',pf,prefs)
        write(blinded/f'{reviewer}_candidate_ratings.csv',rf,ratings)
        write(maps/f'{reviewer}_crosswalk.csv',['family_id','audience','phrasing','display_id','candidate_id'],crosswalk)
    return {r:len(prefs) for r,_,prefs,_,_,_ in prepared}

if __name__=='__main__': print(json.dumps(generate(),indent=2))

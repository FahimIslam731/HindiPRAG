#!/usr/bin/env python3
"""Copy packet-free UI source and existing blinded CSVs to a new private workspace.

Does not regenerate assignments, modify answers, or copy crosswalks to reviewers.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from blind_annotation_packets import read
from prepare_annotation_packets import PREF_FIELDS, RATING_FIELDS

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web/annotation'


def build(packets, output):
    packets, output = Path(packets), Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Interface output must be outside the public repository')
    if output.exists():
        raise FileExistsError(output)
    prepared = []
    for n in (1, 2):
        paths = [packets / f'reviewer_{n}_{suffix}.csv'
                 for suffix in ('preferences', 'candidate_ratings')]
        pf, prefs = read(paths[0]); rf, ratings = read(paths[1])
        if pf != PREF_FIELDS or rf != RATING_FIELDS:
            raise ValueError('Incompatible CSV headers')
        key = lambda r: '|'.join(r[k] for k in ('family_id', 'audience', 'phrasing'))
        grouped = {}
        for row in ratings:
            grouped.setdefault(key(row), []).append(row)
        if len(prefs) != len(grouped) or len({key(r) for r in prefs}) != len(prefs):
            raise ValueError('Duplicate or missing preference contexts')
        for row in prefs:
            candidates = grouped.get(key(row), [])
            if len(candidates) != 3 or {r['candidate_id'] for r in candidates} != {'X1', 'X2', 'X3'}:
                raise ValueError('Each context requires three blinded candidates')
        # Answers remain in CSVs, never prefilled into a distributed reviewer app.
        if any(any(row.get(f) for f in PREF_FIELDS[7:]) for row in prefs) or any(
                any(row.get(f) for f in RATING_FIELDS[9:]) for row in ratings):
            raise ValueError('Only blank packets may be distributed; preserve answered CSVs separately')
        fingerprint = hashlib.sha256(b''.join(p.read_bytes() for p in paths)).hexdigest()
        prepared.append(dict(role=f'reviewer{n}', fingerprint=fingerprint, preferences=prefs,
                             ratings=ratings, grouped=grouped, prefFields=pf, ratingFields=rf))
    output.mkdir(parents=True, mode=0o700)
    coordinator = output / 'coordinator'; coordinator.mkdir(mode=0o700)
    shutil.copy2(WEB / 'dashboard.html', coordinator / 'dashboard.html')
    shutil.copy2(WEB / 'core.js', coordinator / 'core.js')
    for n, packet in enumerate(prepared, 1):
        reviewer = output / f'reviewer{n}'; reviewer.mkdir(mode=0o700)
        for name in ('index.html', 'core.js', 'interface.js'):
            shutil.copy2(WEB / name, reviewer / name)
        content = 'window.PACKET=' + json.dumps(packet, ensure_ascii=True) + ';\n'
        (reviewer / 'packet.js').write_text(content, encoding='utf-8')
        (coordinator / f'packet{n}.js').write_text(content, encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packets', required=True, help='directory of existing blank blinded CSVs')
    parser.add_argument('--output', required=True, help='new private directory outside the repository')
    args = parser.parse_args()
    try:
        print(build(args.packets, args.output))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, f'ERROR: {exc}\n')


if __name__ == '__main__':
    main()

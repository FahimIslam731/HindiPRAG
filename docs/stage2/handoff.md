# Fahim handoff — provisional Stage 2 inputs

**Status: not a frozen release.** No training-ready preference labels or JRA/SC eligibility flags are present. Use the existing research proposal for B2/M1/M2; the dataset supplies three candidates, A informal Hindi, B respectful Hindi, C Gen Z Hinglish. The tags are not human preferences. The preferred member of a three-candidate set alone does not order the other two. The mapping from collected choices to the proposal's pairwise comparison needs explicit clarification.

Inputs: `data/draft/families.jsonl`, `data/splits.json`, `data/generation_subset.json`, `docs/data_schema.md`, `docs/annotation_guide.md`, and the pilot CSV templates. Split manifests list all train, validation and test IDs and the generation subset identifies 30 test families. Preserve each family and its linked contexts/candidates in a single split. Four lexical overlap pairs were conservatively linked; additional group review may be needed.

Minimal read-only example from repository root:

```python
import json
from pathlib import Path
families = [json.loads(line) for line in Path('data/draft/families.jsonl').read_text(encoding='utf-8').splitlines() if line]
splits = json.loads(Path('data/splits.json').read_text(encoding='utf-8'))['splits']
train = [family for family in families if family['family_id'] in set(splits['train'])]
```

Run `python3 scripts/validate_release.py` and `python3 -m unittest discover -s tests -v`. Annotation import and agreement instructions are in `docs/stage2/annotations.md`. An unfrozen source inventory can be prepared with `python3 scripts/prepare_freeze.py --output /tmp/hindiprag-inventory`; exit code 2 indicates blocked, and unknown eligibility is JSON null, not false. The inventory is not a final processed dataset.

Dependencies: obtain real independent preferences for required contexts and training, adjudications and reviewer provenance; resolve pairwise mapping, eligibility and exclusions; then finish and run the release gate. Human generation ratings are a later return handoff after actual model outputs exist.

## Release contract and evaluation inputs

`docs/stage2/freeze.md` specifies the fixed-pair gate. For each family, the research team's approved policy supplies a fixed ordered pair and real pairwise reviewer records supply the outcomes. A true `jra_eligible` requires resolved strict familiar-original preference for the first candidate and respectful-original preference for the second. A true `sc_eligible` additionally requires those same preferences for both paraphrases. A tie, none, unclear, or incompatible direction is an exclusion; the export records reasons. The actual dataset currently has no established eligibility flags or denominators.

When all real inputs pass the documented gate, the versioned release contains:

- `families.jsonl`: objects with the original family under `family` and its partition under `split`.
- `splits.json` and `generation_subset.json`: exact family IDs and source hash.
- `eligibility.jsonl`: pair IDs, resolved context outcomes, boolean JRA/SC flags and exclusion reasons for each family.
- `judgments.json` and `adjudications.json`: source rows, source paths and row numbers; `pairwise_policy.json`: the explicit supplied pair mapping and attestation.
- `manifest.json`: version, input and exported file SHA-256 digests, split-level denominators, exclusion counts, annotation source hashes and limitations.

A future release can be read without any model dependency:

```python
import json
from pathlib import Path
release = Path('releases/VERSION')
manifest = json.loads((release / 'manifest.json').read_text(encoding='utf-8'))
families = [json.loads(line) for line in (release / 'families.jsonl').read_text(encoding='utf-8').splitlines()]
flags = {row['family_id']: row for row in (json.loads(line) for line in (release / 'eligibility.jsonl').read_text(encoding='utf-8').splitlines())}
test_sc = [entry for entry in families if entry['split'] == 'test' and flags[entry['family']['family_id']]['sc_eligible']]
```

The gate's `FROZEN` result reflects mechanical validation, not automatic verification of reviewer identities, independence or research approval. Check those human attestations and the still-provisional near-duplicate grouping before using a release. The existing best-of-three format does not establish the ordering of the two unselected responses. The gate currently accepts directly recorded pairwise outcomes; an approved mapping from existing three-candidate judgments must be documented and any necessary missing comparisons obtained before applying it.

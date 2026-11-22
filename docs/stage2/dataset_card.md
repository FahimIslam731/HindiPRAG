# HindiPRAG dataset card — Stage 2 draft

Release status: **not frozen**. The owner confirms human review and approval of the 200 families and three-candidate design; the repository does not contain the individual semantic-review records. Independent preference annotations, adjudications, agreement and eligibility denominators are not established.

The source `data/draft/families.jsonl` contains 200 families, 192 original groups, two audience contexts with original and paraphrase each, and three Romanized Hindi/Hinglish response candidates. Inputs are English scenarios. A, B and C describe intended candidate style, not preference labels. All original preference placeholders are null. There is no explicit per-family script, style-eligibility or authorship metadata.

`data/splits.json` assigns 120/30/50 train/validation/test families, preserving original groups and four conservatively linked overlap pairs. All pilot families and their linked groups are in training. Further overlap could exist. `data/generation_subset.json` fixes 30 test IDs prior to model output inspection. These allocations do not prove semantic independence.

Run `python3 scripts/validate_release.py` and `python3 -m unittest discover -s tests -v`. To create an **unfrozen**, non-overwriting inventory, run `python3 scripts/prepare_freeze.py --output /tmp/hindiprag-inventory`; exit status 2 indicates the release is blocked. It writes source and output checksums, a split-tagged copy, and unknown eligibility. It deliberately cannot produce a frozen release or infer pairwise labels.

The actual release requires real independent preferences and any necessary adjudications, an approved pairwise mapping, valid coverage and denominator checks, and final provenance. `docs/stage2/freeze.md` documents the tested fixed-pair release gate and its limitations. The inventory is not a training-ready release.

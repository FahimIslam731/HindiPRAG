# M6 annotation handoff

## Reviewer packets and blinding

Distribute only the appropriate privately generated `reviewer1/` or `reviewer2/` folder. The public repository contains reusable source, not operational packets or private crosswalks.

- Reviewer 1: 200 families, 800 contexts and 2,400 candidate ratings.
- Reviewer 2: F001–F024 plus validation and test families, 104 families, 416 contexts and 1,248 candidate ratings.

Each context displays three candidates with local IDs `X1`, `X2`, `X3`. The mapping to stable A/B/C IDs changes between contexts; style labels are omitted. Keep the coordinator folder, source dataset/repository, crosswalks, stable-ID packets and other reviewer answers away from reviewers. Candidate wording can still suggest style; aliases do not guarantee that style is unknowable.

For a new assignment workspace, run from the repository root:

```sh
python3 scripts/prepare_annotation_packets.py
python3 scripts/blind_annotation_packets.py
python3 scripts/build_annotation_interfaces.py \
  --packets ../HindiPRAG-private/blinded \
  --output ../HindiPRAG-private/new-annotation-system
```

The first two commands default to private sibling directories and refuse existing output. The builder accepts existing blank blinded CSVs, rejects answered inputs and refuses output inside this repository. It does not generate or distribute crosswalks. Keep the matching `../HindiPRAG-private/private_maps/` files coordinator-only. Never regenerate or replace an active assignment: original packets, crosswalks and JSON fingerprints must stay matched. Existing private deployments remain valid and need no regeneration.

Open the assigned `index.html` locally. Enter genuine judgments and reviewer ID; progress auto-saves when browser storage is available. Download JSON backups regularly. Restore accepts only the same assignment and asks before replacing existing answers. Export both preference and candidate-rating CSVs; allow both downloads. The import/merge control accepts compatible earlier exports and rejects conflicts atomically. Files with timestamps, error tags or adjudication metadata must instead use the existing import pipeline to preserve those fields. Return files through an agreed private channel to the coordinator; retain original independent first-pass records. Keep both reviewers' answers separate.

The coordinator dashboard loads each reviewer's JSON backup and shows complete, missing, invalid and rating counts. It does not establish independence or calculate adjudications. Browser interaction still requires manual acceptance; see `verification.md`.

Use the existing rubric in `docs/annotation_guide.md`. The file names identify assignment slots, not claimed identities. Choose genuine distinct Hindi-proficient reviewers, document IDs, proficiency, independence and any authorship overlap separately, and keep first-pass records private from each other. Original and paraphrase contexts are separate judgments.

For each preference row, find the three rating rows with the same family ID, audience and phrasing and present them in their given order. Rate each response for meaning fidelity, register fit and naturalness. Record one actual preference (`X1`, `X2` or `X3`), a tie with exact displayed IDs (such as `X1|X3`), `none`, or `unclear`, with a rationale and genuine annotator ID. Use that same ID on the reviewer's rating rows. Record timestamps only if known. Avoid re-sorting candidate rows: it changes their presentation order.

The minimum is 1,216 prompt judgments and 3,648 candidate ratings. The owner has confirmed semantic review of the 200 families; these are preference and rating tasks, not a repeat of that review.

## Import and coverage

The existing annotation importer accepts one blinded packet pair directly when given the corresponding private crosswalk. It converts aliases internally and records the actual input paths and hashes; original reviewer files remain untouched. Completely blank rows in a partially completed packet are skipped, while partially answered rows fail validation:

```sh
python3 scripts/annotations.py --allow-blank \
  --blinded-crosswalk /private/coordinator/reviewer_1_crosswalk.csv \
  --preferences /private/reviewer_1_preferences.csv \
  --ratings /private/reviewer_1_candidate_ratings.csv \
  --output /private/reviewer_1_report.json
```

Repeat with reviewer 2's files and crosswalk. To compute coverage and agreement across both reviewers, convert each pair into a **new private directory**, retaining the conversion manifest and original files:

```sh
python3 scripts/unblind_annotation_packet.py \
  --preferences /private/reviewer_1_preferences.csv \
  --ratings /private/reviewer_1_candidate_ratings.csv \
  --crosswalk /private/coordinator/reviewer_1_crosswalk.csv \
  --output /private/converted_1
python3 scripts/unblind_annotation_packet.py \
  --preferences /private/reviewer_2_preferences.csv \
  --ratings /private/reviewer_2_candidate_ratings.csv \
  --crosswalk /private/coordinator/reviewer_2_crosswalk.csv \
  --output /private/converted_2
python3 scripts/annotation_coverage.py \
  --preferences /private/converted_1/preferences.csv \
  --preferences /private/converted_2/preferences.csv \
  --ratings /private/converted_1/candidate_ratings.csv \
  --ratings /private/converted_2/candidate_ratings.csv \
  --output /private/coverage.json
python3 scripts/annotations.py --allow-blank \
  --preferences /private/converted_1/preferences.csv \
  --preferences /private/converted_2/preferences.csv \
  --ratings /private/converted_1/candidate_ratings.csv \
  --ratings /private/converted_2/candidate_ratings.csv \
  --output /private/combined_annotation_report.json
```

Output files and directories must not already exist. Use an appropriately protected location and do not publish reviewer identities or source files without authorization. Preserve the conversion manifests with the original reviewer records: combined reports reference the converted CSVs, whose manifests link back to original blinded files and crosswalk hashes.

Coverage lists missing prompts and unadjudicated preference disagreements. Distinct IDs alone do not prove independence. Candidate-level rating disagreements require separate human review; they are not included in the preference disagreement list. Follow `docs/stage2/annotations.md` to import real adjudication records; pass `--adjudications /private/adjudications.csv` to the combined commands when available.

The gate in `docs/stage2/freeze.md` additionally requires an explicitly approved fixed-pair policy and directly recorded pairwise outcomes. Best-of-three choices are **not** themselves completed pairwise CSVs. Once the decision in `docs/stage2/candidate_policy_approval.md` is documented, obtain any actual additional comparisons required. Do not fabricate the ordering of the two candidates not selected.

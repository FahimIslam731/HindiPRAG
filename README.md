# HindiPRAG — auditable draft dataset and pilot package

**Status:** **Draft / pre-annotation.** This repository does **not** contain human preference ground truth or completed model experiments. Files here are usable for annotation preparation and structural quality assurance, **not** a claimed validated benchmark.

## What's included

```
data/draft/families.json       # 200 ordered scenario family objects
data/draft/families.jsonl      # same records, one JSON object per line
docs/data_schema.md            # source schema and interpretation
docs/annotation_guide.md       # detailed reviewer instructions and rubric
pilot/issues_log.csv           # 10 issue flags, editable and evidence-backed
pilot/issues_log.md            # readable register and 24-family pilot overview
pilot/pilot_status.csv         # 24 unstarted baseline pilot families
pilot/candidate_ratings_template.csv # 288 blank candidate-rating rows per annotator
pilot/preferences_template.csv       # 96 blank prompt-level choices per annotator
pilot/targeted_review_template.csv   # 6 flagged family reviews, unfilled
scripts/validate_release.py    # standard-library checker
validation_report.md           # automated checks and research limitations
.github/workflows/validate-draft.yml # optional GitHub Actions automated check
```

## Scope and design

- **200 families**, with two English relationship contexts (`familiar`, `respectful`), each with one original English scenario and one English paraphrase.
- **600 candidate response texts** in Romanized Hindi/Hinglish (A informal, B respectful, C Gen Z Hinglish), reused across four presentations per family.
- **192 distinct template-group IDs.** These groups are provisional and require semantic review before group-aware splitting.
- `preference_labels` are `null` in **all 200 families**; this is deliberate and must not be mistaken for preference annotation.
- **No additional Hindi dialogue input field** is part of the current English-scenario-conditioned protocol.

## Run validation

From the repository root, with Python 3.9+:

```bash
python scripts/validate_release.py
```

The script checks record shape, ordering, completeness, candidate tags, JSON/JSONL parity, issue references, blank pilot instruments, and consistency between files. It cannot judge semantics or replace human annotation.

## Pilot workflow

1. Read `docs/annotation_guide.md` and `docs/data_schema.md`.
2. Assign two independent annotators. Make one copy of each blank pilot template per annotator; do not overwrite votes.
3. Annotate F001–F024 (24 baseline families; 96 prompt-level choices + 288 candidate ratings per annotator).
4. Separately inspect six flagged families (F031, F056, F072, F159, F166, F175) using `pilot/targeted_review_template.csv`.
5. Log issues in `pilot/issues_log.csv`; adjudicate and version any changes.
6. Only after real annotation and semantic grouping should you report preferences, agreement, or split-based results.

## Documented limitations

**The 24-family pilot is not yet conducted.** The issues log includes proposals and observable text discrepancies, **not** signed-off human corrections. This package does not claim inter-annotator agreement, model accuracy, a human-validated training set, or final semantic equivalence. The sample of F001–F024 is convenient rather than statistically representative.

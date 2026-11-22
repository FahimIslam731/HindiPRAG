# Annotation import

Keep each reviewer's original completed CSV separate from the distributed blank templates. Use the fields in `pilot/preferences_template.csv` and `pilot/candidate_ratings_template.csv`. Every imported row requires the real annotator ID; preference decisions require the rationale and, for a tie, sorted IDs such as `A|C`. Candidate ratings require valid rubric values. The tool records input paths, SHA-256 hashes and CSV row numbers, preserving original files. Blank template rows are rejected.

Example (paths are examples, not existing labels):

```sh
python3 scripts/annotations.py --preferences reviewer1.csv --preferences reviewer2.csv --ratings ratings1.csv --ratings ratings2.csv --adjudications adjudicated.csv --output annotation-report.json
```

Adjudication uses the preference columns with the real adjudicator in `annotator_id` and an additional `source_reviewers` column containing at least two source reviewer IDs separated by `|`. There can be at most one adjudicated result per prompt. Raw judgments remain separate. The tool validates the references and enforces a different adjudicator; it cannot verify independence, identity, blinding or language proficiency, which require genuine human records.

The report counts covered prompts and complete/incomplete candidate ratings. Agreement is exact agreement and unweighted nominal Cohen's kappa, computed per reviewer pair on shared prompt decisions, with ties represented by their actual candidate sets. Undefined kappa is JSON null. Counts are not an assertion of reviewer independence. Missing preferences are not converted to labels. Best-of-three does not establish an ordering between the two unselected candidates; pairwise use requires the documented research decision.

The M6 blinded randomized packets are described in `docs/stage2/annotation_handoff.md`. Use `--allow-blank` when importing partially completed packets; completely unanswered rows are skipped and partial answers still fail validation. Use `--blinded-crosswalk` with one reviewer packet pair for direct import; keep mappings away from reviewers.

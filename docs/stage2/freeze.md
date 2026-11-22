# Stage 2 freeze gate

The actual release is **blocked**: approved pair mapping, pairwise judgments, independence evidence and any needed adjudications have not been supplied. The owner has approved the three-candidate design and the reviewed examples. This tool does not change either.

The implemented gate supports the proposal's fixed-pair form when actual pairwise judgments are available. It does **not** derive a pairwise relation between the two unselected candidates from a best-of-three choice. The agreed mapping from the existing three-candidate annotations to the pairwise task must be documented by the research team. If those annotations do not explicitly provide the comparisons required by the agreed mapping, obtain the missing information; do not invent it. Other mappings are not automatically supported by this implementation.

## Required inputs

1. A UTF-8 JSON policy with nonempty `version`, `approved_by`, `approval_evidence`, `pairwise_instructions`, `independence_evidence`, and `pairs`. `pairs` maps each family ID to two distinct candidate IDs in fixed order. The first candidate represents the familiar-direction response and the second the respectful-direction response for the proposal's strict reversal calculation. These are policy assignments, not preference labels. Approval and independence fields document human attestations; the program cannot verify their truth.
2. One or more genuine UTF-8 pairwise judgment CSV files with headers `family_id,audience,phrasing,left_id,right_id,outcome,annotator_id,rationale`. `outcome` is `left`, `right`, `tie`, `unclear`, or `none`. Reviewer IDs identify the people who supplied each independent first-pass comparison. A row is required for each of the four contexts of each family: at least two distinct reviewers for every validation/test and pilot context, and at least one for other training contexts. Source records and their SHA-256 digests are preserved in the export.
3. An optional adjudication CSV with the same fields plus `source_reviewers`, a `|`-separated list of at least two source reviewer IDs for that prompt. The adjudicator must be distinct. Disagreements require adjudication; raw judgments remain available separately.
4. The existing source JSONL, split manifest and generation-subset manifest. The gate checks the source hash, unique split assignment, pilot containment, original group isolation, conservative M0 links and the 30-family test subset. Human review of any additional leakage links remains necessary.

For a fixed pair, JRA eligibility requires an independently resolved strict preference for the first candidate in familiar original and the second in respectful original. SC eligibility also requires these preferences in the corresponding paraphrases. Ties, unclear or none decisions do not form strict reversals. The export includes per-family flags, resolved outcomes, exclusion reasons, split-level counts and source hashes. Missing judgments or unresolved reviewer disagreements block the release entirely; they are not treated as labels.

## Execution

After the real inputs and policy are prepared, run from the repository root, replacing the example paths:

```sh
python3 scripts/freeze_release.py --version VERSION --policy policy.json \
  --judgments reviewer1.csv --judgments reviewer2.csv \
  --adjudications adjudications.csv --output releases/VERSION
```

The output directory must not exist. The gate runs the draft validator before writing a release, records the version and hashes, exports families, splits, eligibility, original judgments, adjudications and policy, and exits 0 only on a complete release. A coverage or disagreement blocker exits 2 and creates no output directory; malformed inputs exit 1. A `FROZEN` status attests only that these mechanical gates passed: reviewer independence, policy approval, grouping completeness and human provenance must still be confirmed by the research team.

For an inventory with no labels, `python3 scripts/prepare_freeze.py --output /tmp/hindiprag-inventory` returns blocked and records unknown eligibility; it does not create a release. Tests use synthetic data only in temporary directories.

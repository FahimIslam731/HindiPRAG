# HindiPRAG — validation report

**Validation date:** 2026-11-21 (America/Los_Angeles)  
**Artifact:** `data/draft/families.jsonl`, equivalent JSON array, and supporting pilot/docs files.  
**Scope:** Automated structural and cross-file checks; **not** human semantic adjudication.

## Automated outcomes

| Check | Verified result |
|---|---|
| JSONL parsing | 200/200 records decode successfully |
| JSON/JSONL parity | Identical objects in identical order |
| Family IDs | F001–F200, unique and sequential |
| Candidate inventory | Exactly three per family; 600 total, no blanks |
| Candidate IDs/register tags | A=`informal_hindi`, B=`respectful_hindi`, C=`genz_hinglish`, each 200 |
| Context fields | Both relationship contexts have nonempty original and paraphrase text |
| Exact duplicate original/paraphrase within family | None |
| Template-group IDs | 192 distinct IDs; six are shared by multiple families |
| Preference annotations | No populated labels (`null` in all 200 families) |
| Issues | 10 recorded review flags; six specific families, four dataset-wide |
| Baseline pilot | F001–F024, 24 families, not started |
| Pilot annotation templates | 96 blank prompt-level decisions and 288 blank candidate-level rating records per annotator |
| Targeted family reviews | Six blank review instruments; not yet adjudicated |

## Known open concerns

- **F166:** candidate A may answer a request for a *recommendation* by suggesting a joint change of location; check also candidate C.
- **F175:** candidate C introduces an unstated motivation (`camera mood nahi hai`).
- **F056/F072:** book ownership and package ownership wording warrant checking.
- **F031:** candidate C's actual Gen Z register suitability needs reviewing.
- **F159:** currently about a board game; confirm preservation of the 30-minute late-arrival request.
- **All families:** No completed preference annotation; no group-aware split audit; no human semantic or cultural validation.

## What the report does *not* claim

This validation does not prove that scenarios and paraphrases preserve the same meaning, that responses are culturally/naturally appropriate, that template groups are correct, or that any candidate is a ground-truth preference winner. It does not measure agreement or report model performance. Draft review flags are **not** confirmed corrections.

## Reproduce

From the package root, run:

```bash
python scripts/validate_release.py
```

No third-party Python dependencies are required for this validation script.

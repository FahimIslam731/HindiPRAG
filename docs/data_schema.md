# HindiPRAG draft dataset schema

## Canonical files

- `data/draft/families.jsonl`: UTF-8; **one JSON object per nonempty line**; 200 records.
- `data/draft/families.json`: same 200 objects as a JSON array (pretty-printed).

The two forms must decode to **identical ordered objects**. Neither format contains completed preference annotations.

## Family object

| Field | Type | Notes |
|---|---|---|
| `family_id` | string | Unique `F001` … `F200` |
| `template_group_id` | string | Group proposal, e.g. `TG_001`; **not yet semantic-audited** |
| `topic` | string | Scenario topic code |
| `intent` | string | English description of communicative goal |
| `contexts.familiar` | object | `relationship`, `scenario`, `paraphrase` (all nonempty English strings) |
| `contexts.respectful` | object | Same fields, distinct addressee relationship |
| `candidates` | array of 3 objects | Ordered candidate IDs A, B, C; fields `id`, `register_label`, `text` |
| `preference_labels` | null | Placeholder for **future** human annotations; do not auto-populate with register IDs |

Candidate tags: `A`→`informal_hindi`, `B`→`respectful_hindi`, `C`→`genz_hinglish`. They describe **intended generation style**, not measured register fit or human preference.

Four experiment presentations can be constructed from each family: familiar/scenario, familiar/paraphrase, respectful/scenario, respectful/paraphrase. The candidate list is reused for each presentation.

## Example (schema illustration, not an annotation)

`F002` asks for an explanation of assignment question 3; familiar relationship is `friend`, respectful relationship is `TA`; candidate ratings and preferred response are **unknown** until humans annotate them.

## Validation and data provenance

`python scripts/validate_release.py` checks IDs, required fields, candidate tags, JSON/JSONL parity, issue references, and blank pilot-template labels. This is a **syntactic and cross-file** check only. It does not certify linguistic quality, semantic equivalence, task suitability, cultural validity, or statistical independence.

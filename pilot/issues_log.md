# HindiPRAG — pilot and issues log

**Status: draft review queue; no human-adjudicated findings or pilot results.**

## Evidence and counts

- Canonical source: `data/draft/families.jsonl`.
- 200 unique family IDs; 600 nonempty candidates (200 each A/B/C); 192 template groups.
- 200/200 `preference_labels` are `null`.
- Initial scope: F001–F024 baseline pilot (24 families). All are `not_started`.
- Supplementary targeted review: F031, F056, F072, F159, F166, F175. These six are **outside** the baseline 24.
- Original/paraphrase text fields are distinct within each family. This does **not** establish semantic equivalence.

## Review issue register

| Issue ID | Severity | Family | Evidence-backed question | Status |
|---|---|---|---|---|
| ISS-001 | high | Dataset-wide | 200/200 families have preference_labels=null. | open |
| ISS-002 | high | Dataset-wide | JSON parsing does not establish intent fidelity, register appropriateness, or naturalness. | open |
| ISS-003 | medium | Dataset-wide | 200 families use 192 template groups; 6 groups contain more than one family. | open |
| ISS-004 | low | Dataset-wide | Dataset contexts are English scenarios/paraphrases; candidate outputs are Romanized Hindi/Hinglish. | open |
| ISS-005 | medium | F031 | C: “Group photo aage forward mat karna, please.” Source: ask not to forward group photo. | open |
| ISS-006 | medium | F056 | Respectful context addresses librarian; B: “Kya main aapki kitab ek hafte aur rakh sakta hoon?” | open |
| ISS-007 | medium | F072 | Both friend and speaker expect package; B: “Kya aap mere der se aa rahe package ki sthiti bata sakte hain?” | open |
| ISS-008 | medium | F159 | Current respectful scenario: board-game organizer, joining 30 minutes late; B explicitly mentions board game. | open |
| ISS-009 | high | F166 | Scenario: request another café recommendation; A: “Woh café band hai, koi aur jagah chalein?” | open |
| ISS-010 | medium | F175 | Scenario: opt out of group photo; C: “Group pic mein mujhe skip kar dena, camera mood nahi hai.” | open |

These are **review flags, not confirmed/closed errors**. The CSV is the editable source of record and includes reviewer, resolution, adjudicator, and decision fields; they are blank until real review happens.

## Baseline pilot status

| Baseline family | Template group | Topic | Status |
|---|---|---|---|
| F001 | TG_001 | study_coordination | not_started |
| F002 | TG_002 | study_coordination | not_started |
| F003 | TG_003 | requests | not_started |
| F004 | TG_004 | requests | not_started |
| F005 | TG_005 | apologies | not_started |
| F006 | TG_006 | apologies | not_started |
| F007 | TG_007 | scheduling | not_started |
| F008 | TG_008 | scheduling | not_started |
| F009 | TG_009 | congratulations | not_started |
| F010 | TG_010 | disappointment | not_started |
| F011 | TG_001 | study_coordination | not_started |
| F012 | TG_012 | study_coordination | not_started |
| F013 | TG_013 | requests | not_started |
| F014 | TG_014 | requests | not_started |
| F015 | TG_015 | apologies | not_started |
| F016 | TG_016 | apologies | not_started |
| F017 | TG_017 | scheduling | not_started |
| F018 | TG_018 | scheduling | not_started |
| F019 | TG_009 | congratulations | not_started |
| F020 | TG_009 | congratulations | not_started |
| F021 | TG_009 | congratulations | not_started |
| F022 | TG_010 | disappointment | not_started |
| F023 | TG_023 | disappointment | not_started |
| F024 | TG_024 | disappointment | not_started |

## Triage priorities

1. **Blocker:** Collect actual preference judgments (`ISS-001`) and human semantic review (`ISS-002`) before describing the dataset as labeled, training-ready, or validated.
2. **High risk:** Check whether F166 changes a recommendation request into an alternative plan (`ISS-009`).
3. **Other targeted checks:** Inspect F175 unsupported reason, F056 borrowed-book ownership, F072 shared-package pronouns, F031 style adequacy, and F159 restored board-game consistency.
4. **Dataset design:** `ISS-004` is a documentation clarification, not a requirement to create separate Hindi dialogue inputs.
5. **Leakage protection:** Audit template groups and near-duplicates (`ISS-003`) before creating evaluation splits.

## Resolution workflow

Assign a reviewer → inspect exact scenario and candidate text → record evidence and proposed correction → adjudicate with a second/third reviewer → apply an approved change in a versioned data file → add regression check → mark status resolved.

Blank templates are provided in `pilot/candidate_ratings_template.csv` (288 candidate-level rows), `pilot/preferences_template.csv` (96 prompt-level rows), and `pilot/targeted_review_template.csv` (6 families). No scores have been fabricated.

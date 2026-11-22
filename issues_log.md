# HindiPRAG — Pilot and Issues Log

**Status:** Draft / review queue (not an adjudicated annotation report).

## Source and scope

- Source: `data/draft/families.json` exported from the HindiPRAG workbook.
- 200 families, 600 response candidates, 192 distinct template-group IDs.
- `preference_labels` is `null` for all 200 families. Register labels indicate candidate style, not annotator preference.
- Pilot proposal: F001–F024 (24 families), **not yet reviewed**.

## Pilot tracking

| Family | Template group | Topic | Review status | Preference annotation |
|---|---|---|---|---|
| F001 | TG_001 | study_coordination | Not started | Missing |
| F002 | TG_002 | study_coordination | Not started | Missing |
| F003 | TG_003 | requests | Not started | Missing |
| F004 | TG_004 | requests | Not started | Missing |
| F005 | TG_005 | apologies | Not started | Missing |
| F006 | TG_006 | apologies | Not started | Missing |
| F007 | TG_007 | scheduling | Not started | Missing |
| F008 | TG_008 | scheduling | Not started | Missing |
| F009 | TG_009 | congratulations | Not started | Missing |
| F010 | TG_010 | disappointment | Not started | Missing |
| F011 | TG_001 | study_coordination | Not started | Missing |
| F012 | TG_012 | study_coordination | Not started | Missing |
| F013 | TG_013 | requests | Not started | Missing |
| F014 | TG_014 | requests | Not started | Missing |
| F015 | TG_015 | apologies | Not started | Missing |
| F016 | TG_016 | apologies | Not started | Missing |
| F017 | TG_017 | scheduling | Not started | Missing |
| F018 | TG_018 | scheduling | Not started | Missing |
| F019 | TG_009 | congratulations | Not started | Missing |
| F020 | TG_009 | congratulations | Not started | Missing |
| F021 | TG_009 | congratulations | Not started | Missing |
| F022 | TG_010 | disappointment | Not started | Missing |
| F023 | TG_023 | disappointment | Not started | Missing |
| F024 | TG_024 | disappointment | Not started | Missing |

## Issue register

| ID | Severity | Family(s) | Issue | Status |
|---|---|---|---|---|
| ISS-001 | high | Dataset-wide | No independently collected preference judgments in the JSON dataset. | open |
| ISS-002 | high | Dataset-wide | All families still require an explicit human semantic review before final training use. | open |
| ISS-003 | medium | Dataset-wide | Template grouping needs a semantic audit. | open |
| ISS-004 | medium | Dataset-wide | English scenario inputs are present, but there are no separate Hindi/Hinglish utterance inputs. | open |
| ISS-005 | medium | F031 | Privacy-request candidate C is now on topic, but semantic equivalence and appropriate Gen Z register still need a human check. | open |
| ISS-006 | medium | F056 | Earlier revisions changed who borrowed the book; ownership/relationship alignment should be rechecked. | open |
| ISS-007 | medium | F072 | A shared delayed-package context may conflict with a first-person ownership reference in the respectful candidate. | open |
| ISS-008 | medium | F159 | Earlier versions changed the activity from a board game to a workshop. | open |
| ISS-009 | medium | F166 | Earlier versions changed a closed café into an unavailable meeting room. | open |
| ISS-010 | medium | F175 | A candidate may introduce an unsupported reason (camera mood). | open |

## Review protocol

For each pilot family, verify (1) identical communicative intent across familiar/respectful contexts, (2) faithful paraphrases, (3) response appropriateness and naturalness, (4) absence of invented facts, (5) candidate register alignment, and (6) preference labels only after independent annotation. Record reviewer, date, issue ID, correction, and adjudication.

## Evidence caveat

The targeted family checks above are **review flags**, not confirmed errors in the current JSON. No human semantic judgments have been fabricated. Full issue details and supporting source text are in `issues_log.csv`.

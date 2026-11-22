# HindiPRAG annotation guide

**Version:** 1.0-draft  
**Status:** Protocol ready for pilot; **no human annotations are claimed**.  
**Dataset:** `data/draft/families.jsonl` (the equivalent array lives in `families.json`).

## 1. Study question and task boundary

HindiPRAG examines **pragmatic register appropriateness** while trying to preserve the same communicative intent across audience relationships and English paraphrases. An annotator sees an **English situation** and chooses among three Romanized Hindi/Hinglish responses. The goal is not free-form machine translation or evaluation of a separately supplied Hindi dialogue turn. **No separate Hindi dialogue input is required by the current dataset design.** Do not add one silently.

For one family, the available independent variables are:

- **Audience/context:** `familiar` or `respectful` (specific addressee relationship appears in each context).
- **Phrasing:** `scenario` or `paraphrase` in English, intended to express the same essential act and facts within that audience.
- **Candidate response:** A, B, C, with preassigned *style tags* only: A=`informal_hindi`; B=`respectful_hindi`; C=`genz_hinglish`.

The candidate IDs and style tags are **not** human-assessed register success and are **not** correct-answer labels. Do not choose B automatically for respectful situations or C for younger speakers; evaluate what each **actual response** says.

## 2. Annotation unit and required records

Annotate each `(family_id, audience, phrasing)` separately, presenting its **three identical candidate texts** in randomized screen order, with a stable hidden mapping to A/B/C. Each family yields **4 prompt presentations** (2 audiences × 2 phrasings) and **12 candidate ratings** (4 presentations × 3 candidates).

Use two linked output types rather than mixing levels:

1. **Candidate-level ratings**, one record per `(annotator_id, family_id, audience, phrasing, candidate_id)`, stored in `pilot/candidate_ratings_template.csv`.
2. **Prompt-level preference**, one record per `(annotator_id, family_id, audience, phrasing)`, stored in `pilot/preferences_template.csv`.

The distributed CSV templates are **blank, with no invented annotation scores**. Copy them once per annotator (or append a second annotator's rows); do not overwrite the first person's independent decisions.

## 3. Rating rubric

Read the English situation, its relationship, and only the current prompt phrasing. For each candidate, assign:

| Dimension | Allowed values | Decision rule |
|---|---|---|
| `meaning_fidelity` | `pass`, `minor_issue`, `major_issue`, `unclear` | Does it preserve the intended speech act, relevant people, timing, objects, commitments, and polarity? `major_issue` if it changes the requested action, speaker/addressee, deadline, or essential fact. `minor_issue` if the core act survives but an unnecessary detail or nuance changes. `unclear` if insufficient information. |
| `register_fit` | `appropriate`, `borderline`, `inappropriate`, `unclear` | Does its actual address form, politeness, pronouns, slang, and tone fit the specified relationship? Code-mixing alone is **not** an error. |
| `naturalness_1_to_5` | Integer 1–5 | 1=very unnatural; 2=awkward; 3=usable; 4=natural; 5=very natural as Romanized Hindi/Hinglish. |
| `error_tags` | Optional pipe-separated list | `speech_act_change`, `entity_change`, `time_change`, `polarity_change`, `unsupported_detail`, `ownership_change`, `register_mismatch`, `unnatural`, `other`. |
| `rationale` | Short free text | Quote the relevant response span and explain the judgment, especially for any non-pass or inappropriate score. |

**Examples of warning signs grounded in this dataset:** F166 asks for an alternate café **recommendation**, while candidate A may instead suggest going somewhere else; F175 candidate C mentions “camera mood nahi hai” without that reason being present in the English situation. Both are review flags, **not completed human judgments**.

## 4. Select one prompt-level preference

After scoring all three candidates against the **same presentation**, use this precedence:

1. Exclude candidates with `major_issue` when any meaning-faithful candidate is available. Favor faithful speech act and facts over stylistic flair.
2. Prefer the response most appropriate for the actual addressee; compare naturalness as a secondary consideration.
3. Record a decision in `preferred_candidate_id`: `A`, `B`, `C`, `tie`, `none`, or `unclear`.
   - `A/B/C`: one best candidate; leave `tied_candidate_ids` blank.
   - `tie`: a genuine tie among acceptable answers; list involved IDs in alphabetical order joined by `|`, e.g. `A|C`. Do not use `tie` to mean indecision.
   - `none`: all three are seriously unsuitable or fail to express the core speech act.
   - `unclear`: the prompt itself is ambiguous or reviewer cannot confidently judge; describe why.
4. Add an explicit `decision_rationale` even for a tie, none, or unclear result.

A register tag does **not** predetermine the winner. A candidate can be styled as informal and still be preferred in a respectful situation only if its real wording is appropriate.

## 5. Original/paraphrase consistency

Rate the original and paraphrase independently (blinded order recommended). Then compare within each audience:

- Do they preserve the same required action, entities, timing, and constraints?
- Do preferences change for reasons attributable solely to superficial wording?
- If the paraphrase **changes facts**, raise a data issue; do **not** score instability as though it were a valid paraphrase robustness test.

Comparisons across familiar vs respectful audiences are about the relationship's effect, **not** an expectation of an identical preferred candidate.

## 6. Pilot and adjudication procedure

- **Baseline pilot:** F001–F024 (24 families), currently `not_started`. This is a convenience sample; do not claim representativeness. It gives 96 prompt presentations and 288 candidate ratings **per annotator**.
- **Separate targeted audit:** F031, F056, F072, F159, F166, F175 (6 flagged families) in `pilot/targeted_review_template.csv`. These are not quietly counted among the baseline 24.
- **Independent annotation:** Two annotators work without seeing each other's judgments, the register ID labels during display, or any “expected answer.” Record reviewer IDs and ISO-8601 timestamps only for real work.
- **Escalation:** Compare responses. Resolve disagreements on fidelity, register, preference, or paraphrase equivalence with a third reviewer. Retain both original votes and an adjudicated result separately; no overwrite.
- **Corrections:** Record any proposed content change in `pilot/issues_log.csv`, with evidence, reviewer, rationale, and adjudication. Modify dataset only after approval; retain a versioned original.
- **Reporting:** Measure agreement only after collecting ratings. Report denominator and annotation unit; do not invent scores, preference distributions, Cohen's κ, model performance, or human validation percentages.

## 7. Known limitations and leakage prevention

The current 200-family draft has no human preference ground truth. The schema register tag is not a label of success. Six template groups contain multiple families, and other near-duplicates may exist across distinct groups. Before training, audit grouping and split **by approved semantic group**, never randomize variants of a family across different train/test sets. All four presentations and all candidates from one family must remain together.

## 8. Reference files

- `docs/data_schema.md`: JSON schema definitions and file contract
- `pilot/pilot_status.csv`: baseline pilot tracking
- `pilot/candidate_ratings_template.csv` and `pilot/preferences_template.csv`: blank annotation instruments
- `pilot/targeted_review_template.csv`: six issue-focused reviews
- `pilot/issues_log.csv` and `pilot/issues_log.md`: evidence-backed issue register
- `scripts/validate_release.py`: structural and cross-file validation

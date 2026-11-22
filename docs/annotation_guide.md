# HindiPRAG annotation guide — draft v0.1

## Goal
Judge whether Romanized Hindi/Hinglish candidate responses preserve the meaning of an **English scenario** and fit the addressee's relationship. No separate Hindi dialogue input is required.

## Dataset schema
Each family has `family_id`, `template_group_id`, `topic`, `intent`, familiar and respectful contexts (relationship, scenario, paraphrase), and candidates A (informal Hindi), B (respectful Hindi), C (Gen Z Hinglish). These are **register labels**, not preference votes. `preference_labels` remains null until annotation.

## Annotation unit
For each family, annotate four scenario presentations: familiar/original, familiar/paraphrase, respectful/original, respectful/paraphrase. Show all three candidate texts in randomized display order while retaining their IDs internally.

## Rubric
1. **Meaning fidelity:** `pass`, `minor_issue`, `major_issue`, `unclear`. Check action, participants, timing, conditions, and invented reasons.
2. **Register fit:** `appropriate`, `borderline`, `inappropriate`, `unclear`.
3. **Naturalness:** 1–5 (1 unnatural; 5 very natural).
4. **Preference:** choose `A`, `B`, `C`, `tie`, or `none`. Prioritize meaning fidelity, then register, then naturalness. Add a rationale. If all candidates have major fidelity errors, choose `none`.
5. **Paraphrase stability:** compare the independently annotated winners for original vs. paraphrase; flag genuine ambiguity rather than forcing agreement.

## Pilot procedure
Use F001–F024 as a **provisional convenience pilot**, not a representative sample. Obtain two independent blinded annotations per prompt. Send disagreements, major fidelity errors, and unclear cases to a third reviewer. Retain raw and adjudicated decisions separately.

## Suggested annotation record
`family_id,context_type,variant,candidate_id,meaning_fidelity,register_fit,naturalness_1to5,preferred_candidate_id,rationale,annotator_id,annotated_at,review_status`

## Review flags
- F072: jointly expected package versus `mere ... package`.
- F175: candidate C adds `camera mood nahi hai`, absent from the scenario.
- F056: confirm book ownership and librarian phrasing.
- F166: candidate A proposes going elsewhere instead of clearly requesting a recommendation.
- F031 and F159: verify previously corrected scenarios.

## Quality and leakage controls
Do not infer preferences from candidate register labels. Review near-duplicate template groups before train/validation/test splits. Record issue evidence and adjudication in the pilot log. Do not report annotator agreement or model accuracy until measured.

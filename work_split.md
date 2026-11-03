# HindiPRAG work split

Proposed allocation for **Varun, Devarchitch, and Fahim**, based on the revised HindiPRAG proposal. This is a plan for the team to review, not a record of completed work. Dates should be set against the course deadline.

## Recommended order

**Varun builds the scenario set → Devarchitch validates and freezes the data → Fahim builds the models, runs the experiments, and writes the report.**

This gives each stage one accountable owner and a concrete handoff. Fahim takes the largest share of coding and report writing and has no campus-dependent responsibilities. Varun and Devarchitch own participant coordination, any in-person review, and the final live presentation.

A completely strict sequence would not fit the proposal: validation/test labels require two independent Hindi-proficient reviewers, and the generated-response evaluation needs human ratings after inference. Keep those two short review windows, plus an early pilot check, while making the main work sequential. Authored scenarios can be reviewed remotely; collecting real conversations is not required.

| Person | Main ownership | Later commitment |
| --- | --- | --- |
| Varun — stage 1 | Scenario design, original examples, annotation materials, reviewer coordination | Independent reviewing where appropriate, generated-response ratings, live presentation |
| Devarchitch — stage 2 | Dataset quality, annotation process, adjudication records, leakage-safe splits, dataset documentation | Generated-response rating coordination, results review, live presentation |
| Fahim — stage 3 | All core implementation, reproducible experiments, statistical analysis, majority of final report, initial slide deck | Remote technical handoff and presentation rehearsal support |

## Stage 1 — Varun: build the scenario set

**Goal:** give Devarchitch a complete, consistently structured draft dataset and a workable review process.

1. Write annotation instructions covering register appropriateness, preserved intent/facts, naturalness, ties, and culturally ambiguous cases. Reviewers must judge complete responses, not just pronouns or slang.
2. Start with **24 pilot families reserved for training**. Each family has familiar and respectful relationship contexts, one meaning-preserving paraphrase of each context, and two meaning-matched, full-sentence response candidates in different registers.
3. Have Devarchitch check the pilot's clarity and reviewer workload. Give Fahim the pilot for a small CPU/inference feasibility check before scaling up. This is a brief checkpoint, not the full modeling stage.
4. Expand to approximately **200 original families**, covering study coordination, requests, apologies, scheduling, congratulations, and disappointment. Around one-third should permit natural informal Hinglish; Devanagari and Romanized forms are allowed.
5. Assign family IDs and broader template/near-duplicate group IDs. Record topic, relationship, optional style, script, and authorship. Keep all four contextualized prompts and both candidate sentences linked to their family.
6. Coordinate access to **two Hindi-proficient reviewers** for validation/test labels and later generated-response ratings. Varun and Devarchitch may serve if proficient; otherwise recruit suitable reviewers. Preserve independent first-pass judgments and flag authorship overlap rather than implying fully external review.

Use newly authored examples. Do not collect private chats or copy unlicensed dialogue. Any in-person coordination belongs to Varun and Devarchitch, not Fahim.

**Suggested handoff:** `data/draft/families.jsonl`, `docs/annotation_guide.md`, and a pilot/issues log. These are proposed future files, not existing artifacts.

**Done when:** all intended families are present, fields and IDs are consistent, the pilot is approved, and reviewer availability is confirmed. Draft register tags are design intent; they are not validated preference labels.

## Stage 2 — Devarchitch: validate, label, and freeze the data

**Goal:** give Fahim a usable dataset with trustworthy labels, explicit exclusions, and fixed evaluation boundaries.

1. Check that each candidate pair preserves the same communicative act and facts, relationship changes are meaningful, and paraphrases preserve the original relationship and intent. Repair awkward examples before the final labeling pass.
2. Group near-duplicate templates/intentions before splitting. Target **120 train / 30 validation / 50 test families**, keeping the 24 pilot families in training. Keep related templates in one partition; if group sizes prevent exact counts, document the final counts instead of breaking a group apart.
3. Obtain preferences for training examples and **two independent Hindi-proficient judgments for every validation/test context, including paraphrases**. Randomize candidate display order, record ties/ambiguity, and retain the original judgments before adjudication. Varun provides the second review where appropriate; neither reviewer sees the other's first-pass labels.
4. Record adjudication decisions and reviewer agreement. Exclude tied/ambiguous contexts from binary preference supervision. Mark which families satisfy the strict reversal criteria and which have valid paraphrase labels for selective-consistency evaluation; do not manufacture reversals to reach a target count.
5. Freeze the split manifest, labels, eligibility flags, and dataset version. Record counts, exclusions, topic/style coverage, and known limitations. Fahim must use validation families for tuning and keep test labels out of model-development decisions.
6. Prespecify the **30-family held-out generation subset** before inspecting model outputs. Prepare the blinded rating form for social appropriateness, semantic/intent fidelity, and naturalness, including a documented scale and tie handling.
7. If retaining the supporting sentiment experiment, provide positive/neutral/negative utterance labels with grouped partitions and a labeling guide. If that work is infeasible, agree on and document the scope reduction before Fahim implements it; never infer sentiment from the preferred register.

**Suggested handoff:** `data/processed/families.jsonl`, raw and adjudicated annotations, `data/splits.json`, `data/generation_subset.json`, `docs/dataset_card.md`, and the generation rating guide. A documented CSV layout is also fine if it preserves the same links.

**Minimum data contract:** stable family and template-group IDs; split; both relationship contexts and their paraphrases; both full-sentence candidates; topic/style/script metadata; context-level reviewer preferences; tie/ambiguity flags; adjudicated decisions; and evaluation eligibility with exclusion reasons. Keep individual reviewer judgments separate from final labels.

**Done when:** Fahim can load the frozen files without guessing how labels map to contexts, and the split, denominators, exclusions, and rating protocol are documented. Devarchitch also supplies a short dataset/methods write-up for the final report.

## Stage 3 — Fahim: implement, evaluate, and write

**Goal:** turn the frozen dataset into reproducible results and the final written submission, entirely remotely.

1. Set up CPU-capable Python/Colab execution, dependencies, configurations, fixed seeds, data checks, and saved outputs. Validate family links, split isolation, and label eligibility before training.
2. Implement shared character n-gram features and relationship/style–response interactions, with preprocessing fit on training data only. Implement **B1**, the relationship-to-register heuristic, and the matched rankers:
   - **B2:** pairwise logistic preference loss plus L2 regularization.
   - **M1:** B2 plus reversal-margin loss.
   - **M2:** M1 plus paraphrase-invariance loss.
3. Keep B2/M1/M2 training examples and feature representations identical. Tune hyperparameters on validation families only. Check loss behavior, preference signs, and metric calculations with small known examples.
4. Run the primary controlled selection evaluation. Report **joint reversal accuracy (JRA)** and **selective consistency (SC)**, with the main comparison **M2 vs. M1 on SC** and JRA checked for tradeoffs. Report family counts, exclusions, relationship-specific errors, paired exact McNemar tests, and family-cluster bootstrap 95% confidence intervals. Use a common eligible family set for each paired comparison.
5. Run the secondary generation check with **Qwen/Qwen3-0.6B in non-thinking mode**. Cache up to three responses per context and compare **B0 direct output, M1 reranking, and M2 reranking** using the same pools. Define the direct-output selection rule in advance, cap generation at 64 new tokens, and record runtime/memory. Hand anonymized, shuffled outputs to the reviewers.
6. Integrate returned human ratings and report agreement and differences in appropriateness, fidelity, and naturalness. If retained, implement the TF–IDF/logistic-regression sentiment classifier, macro-F1/confusion matrix, and with/without-predicted-sentiment ablation without test leakage.
7. Write the majority of the final report: method, experiments, results, discussion, limitations, and reproducibility instructions. Incorporate Devarchitch's dataset section and both teammates' language judgments. Update the proposal's author block with all three students' confirmed details; do not invent missing details.
8. Prepare the initial slide deck, figures, and a runnable demo or cached examples. Give Varun and Devarchitch speaker notes and a technical walkthrough for the live presentation.

**Suggested handoff:** source code/notebooks, dependency file, run instructions, experiment configurations, cached generation, results tables/figures, final LaTeX report, and slides.

**Done when:** the documented workflow reproduces the reported results, all reported numbers have saved supporting outputs, the report states limitations and deviations, and the presenters can explain the study without Fahim attending in person.

## Required return handoff: human ratings and presentation

After Fahim generates outputs, **Devarchitch coordinates and Varun participates in the blinded rating round**, with another Hindi-proficient reviewer if needed. The planned workload is **30 families × 2 relationships × 3 systems × 2 raters = 360 response-level ratings**; each rating covers the three evaluation dimensions. Return the completed ratings and unresolved issues to Fahim for analysis. Fahim owns final tables and report integration.

**Varun presents** the motivation, examples, and data construction. **Devarchitch presents** the method, results, and limitations, using Fahim's notes. Both handle live questions and rehearse the technical sections. Fahim supports preparation remotely and is not assigned a live presentation slot.

## Milestones and scope control

| Gate | Owner | Requirement before advancing |
| --- | --- | --- |
| Pilot approved | Varun, with brief Devarchitch/Fahim checks | 24 training families, clear instructions, measured review effort and inference feasibility |
| Draft delivered | Varun | Approximately 200 structured families and confirmed reviewers |
| Dataset frozen | Devarchitch | Reviewed labels, grouped splits, exclusions, generation subset, data documentation |
| Core results ready | Fahim | Matched B2/M1/M2 comparison, checked metrics, uncertainty estimates |
| Ratings returned | Devarchitch + Varun/reviewers | Blinded generation ratings ready for analysis |
| Submission ready | Fahim; Varun + Devarchitch for live delivery | Final report, reproducible artifacts, slides, and rehearsal |

Set dates for these gates together, reserving time after inference for the rating return and after analysis for report review and rehearsal. Stage 3 is deliberately the largest stage; do not allocate equal calendar time to each person by default.

Protect the primary controlled selection study if time or compute runs short. Reduce the secondary generation sample if inference is too slow and report the actual sample and limitation, as the proposal allows. Treat sentiment as supporting work, not a substitute for the main experiment. Do not add LLM fine-tuning, paid APIs, or guaranteed GPU dependencies. Report negative or inconclusive findings honestly; the hypothesis does not require M2 to win.

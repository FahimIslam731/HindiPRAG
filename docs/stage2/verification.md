# Final engineering verification

Software status: **annotation-ready**. Dataset: **not frozen**, with zero genuine preference judgments or candidate assessments collected.

Commands run from the clean integration checkout:

```sh
python3 -B scripts/validate_release.py
python3 -B -m unittest discover -s tests -v
node --check web/annotation/core.js
node --check web/annotation/interface.js
git diff --check
```

The validator passes. The 31 unittest cases include the existing 27 repository tests and four interface integration cases. Synthetic fixtures exercise all 1,216 assigned contexts and 3,648 ratings through JSON serialization/restore, ten-family merging, conflict preservation, export, the existing importer and combined coverage. Coordinator event handlers are tested with isolated file/DOM stubs for blank and full coverage. Tests cover crosswalk bijections, randomized alias assignments, tampered source rejection, group/split leakage, and successful/blocked freeze gates. No synthetic answers are retained or used as real annotations.

Confirmed defect fixed: malformed JSON answer/rating types could pass backup validation and crash the reviewer/coordinator dashboard. Invalid structures are now rejected before replacing current progress. Blinding tests now create their packet inputs in temporary directories instead of depending on private tracked artifacts. Generated packet defaults point outside the repository; reusable UI source is packet-free.

## Browser verification limit and manual acceptance

An actual attempt to open the local reviewer interface through browser automation was blocked by the browser URL security policy. No interactive browser success is claimed. JavaScript syntax and isolated handler tests do not establish actual browser rendering, autosave, downloads or file-picker behavior.

Before assigning reviewers, use a disposable copy of each reviewer folder and coordinator dashboard with isolated browser storage. Keep synthetic acceptance answers in that disposable copy only:

1. Confirm 200 families / 800 context options for Reviewer 1 and 104 families / 416 options for Reviewer 2; navigate to first, middle and last contexts. Each must show three X aliases and no stable IDs or style tags.
2. Enter a synthetic reviewer ID and all rubric values, rationale and preference; try a tie with exact members, none and unclear. Confirm complete/invalid totals and navigation behavior.
3. Reload and confirm autosave. Download a JSON backup, restore it into the same disposable assignment, and confirm counts/values. Cancel replacement once; try a wrong-role or malformed backup and verify current answers survive.
4. Export both CSV downloads; import them with the matching private crosswalk using the documented command. Confirm the browser permits both files and UTF-8 text/rationale survives.
5. Merge compatible ten-family exports. Check the 40 contexts and 120 ratings, then attempt a conflicting merge and verify existing progress survives. Preserve timestamp/error-tag records using the CLI pipeline.
6. Load separate Reviewer 1/2 JSON backups into the coordinator. Check required totals of 800, 416 and 1,216, completed/missing/invalid counts and 3,648 rating slots. Same-reviewer IDs must show the independence warning.
7. Delete only disposable acceptance copies and synthetic downloads after recording results. Do not enter acceptance fixtures in a real reviewer's active browser state.

## Publication privacy

The original 11 outgoing development commits include operational annotation packets and private crosswalks. That branch is not suitable for pushing. Integration uses a fresh branch from current main, with no contaminated commit ancestry. No deletion commits from the separate draft branch are included. Approved dataset files, the proposal and `work_split.md` remain byte-identical to main. The original local branch remains available for recovery; it must not be pushed.

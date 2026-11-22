#!/usr/bin/env python3
"""Structural, cross-file, and template checks for the HindiPRAG draft.

Standard library only. Does NOT measure human preference agreement, linguistic
correctness, paraphrase equivalence, or model performance.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ERR = []

def require(ok, message):
    if not ok:
        ERR.append(message)

def read_csv(relative):
    with (ROOT / relative).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def main():
    jsonl = ROOT / "data/draft/families.jsonl"
    try:
        lines = [line for line in jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
        records = [json.loads(line) for line in lines]
        array = json.loads((ROOT / "data/draft/families.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"FAIL: Could not read/parse draft dataset: {exc}")
        return 1

    require(records == array, "JSON and JSONL records differ or their order differs")
    require(len(records) == 200, f"Expected 200 families; found {len(records)}")
    ids = [r.get("family_id") for r in records]
    require(ids == [f"F{i:03d}" for i in range(1, 201)], "Family IDs must be exactly ordered F001-F200")
    require(len(ids) == len(set(ids)), "Repeated family_id values")
    group_ids = [r.get("template_group_id") for r in records]
    require(len(set(group_ids)) == 192, f"Unexpected template-group count: {len(set(group_ids))}")
    require(all(nonempty(v) for v in group_ids), "Some template groups are missing")

    expected_fields = {"family_id", "template_group_id", "topic", "intent", "contexts", "candidates", "preference_labels"}
    target_registers = {"A": "informal_hindi", "B": "respectful_hindi", "C": "genz_hinglish"}
    for i, rec in enumerate(records):
        fid = rec.get("family_id", f"line-{i + 1}")
        require(set(rec) == expected_fields, f"{fid}: unexpected or missing top-level field(s)")
        require(nonempty(rec.get("topic")) and nonempty(rec.get("intent")), f"{fid}: missing topic/intent")
        require(rec.get("preference_labels") is None, f"{fid}: preference_labels changed from null; re-review documentation")
        contexts = rec.get("contexts")
        if not isinstance(contexts, dict):
            ERR.append(f"{fid}: contexts not an object")
        else:
            require(set(contexts) == {"familiar", "respectful"}, f"{fid}: contexts must be familiar/respectful")
            for audience in ("familiar", "respectful"):
                ctx = contexts.get(audience, {})
                require(isinstance(ctx, dict) and set(ctx) == {"relationship", "scenario", "paraphrase"}, f"{fid}/{audience}: context fields incorrect")
                if isinstance(ctx, dict):
                    for k in ("relationship", "scenario", "paraphrase"):
                        require(nonempty(ctx.get(k)), f"{fid}/{audience}: empty {k}")
                    if isinstance(ctx.get("scenario"), str) and isinstance(ctx.get("paraphrase"), str):
                        require(ctx["scenario"].strip().casefold() != ctx["paraphrase"].strip().casefold(), f"{fid}/{audience}: original and paraphrase exactly duplicate")
        candidates = rec.get("candidates")
        if not isinstance(candidates, list):
            ERR.append(f"{fid}: candidates not a list")
            continue
        require(len(candidates) == 3, f"{fid}: expected 3 candidates")
        require([c.get("id") for c in candidates if isinstance(c, dict)] == ["A", "B", "C"], f"{fid}: invalid candidate ordering")
        txts=[]
        for c in candidates:
            if not isinstance(c, dict):
                ERR.append(f"{fid}: candidate not an object")
                continue
            require(set(c) == {"id", "register_label", "text"}, f"{fid}: candidate fields incorrect")
            require(c.get("register_label") == target_registers.get(c.get("id")), f"{fid}: incorrect register tag")
            require(nonempty(c.get("text")), f"{fid}: empty candidate response")
            txts.append(str(c.get("text", "")).strip().casefold())
        require(len(set(txts)) == 3, f"{fid}: identical candidate texts within family")

    issues = read_csv("pilot/issues_log.csv")
    issue_ids = [x["issue_id"] for x in issues]
    require(len(issues) == 10, f"Expected 10 tracked issues; found {len(issues)}")
    require(set(issue_ids) == {f"ISS-{i:03d}" for i in range(1,11)}, "Issue IDs are missing or duplicated")
    require(all(x["status"] == "open" for x in issues), "An issue status was changed without updating the draft review record")
    require(all(not x["reviewed_by"] and not x["adjudicated_by"] for x in issues), "Review metadata populated unexpectedly")
    require(all(x["family_id"] in set(ids) for x in issues if x["family_id"]), "Issue tracker refers to unknown family IDs")
    # Confirm that high-risk review flags still refer to the actual text in this draft.
    by_id = {r["family_id"]: r for r in records}
    flagged_evidence = {
        "F031": ("group photo", "forward"),
        "F056": ("book", "aapki kitab"),
        "F072": ("package", "mere der se"),
        "F159": ("board game", "board game"),
        "F166": ("café", "koi aur jagah chalein"),
        "F175": ("group photo", "camera mood nahi hai"),
    }
    for fid, (scenario_fragment, candidate_fragment) in flagged_evidence.items():
        rec = by_id.get(fid, {})
        scenes = " ".join(c.get("scenario", "") for c in rec.get("contexts", {}).values()).casefold()
        candidates_text = " ".join(c.get("text", "") for c in rec.get("candidates", [])).casefold()
        require(scenario_fragment.casefold() in scenes, f"{fid}: issue scenario evidence is stale")
        require(candidate_fragment.casefold() in candidates_text, f"{fid}: issue response evidence is stale")
    target_ids = {x["family_id"] for x in issues if x["family_id"]}
    require(target_ids == {"F031", "F056", "F072", "F159", "F166", "F175"}, "Unexpected targeted-review family set")

    status = read_csv("pilot/pilot_status.csv")
    require(len(status) == 24, "pilot_status.csv must have 24 families")
    require([x["family_id"] for x in status] == [f"F{i:03d}" for i in range(1,25)], "Pilot selection changed")
    require(all(x["status"] == "not_started" for x in status), "Pilot status changed but results were not verified")

    rating = read_csv("pilot/candidate_ratings_template.csv")
    pref = read_csv("pilot/preferences_template.csv")
    require(len(rating) == 24*2*2*3, f"Expected 288 blank ratings; found {len(rating)}")
    require(len(pref) == 24*2*2, f"Expected 96 blank preferences; found {len(pref)}")
    key4 = lambda x: (x["family_id"], x["audience"], x["phrasing"], x["candidate_id"])
    key3 = lambda x: (x["family_id"], x["audience"], x["phrasing"])
    require(len({key4(x) for x in rating}) == len(rating), "Duplicate template rating keys")
    require(len({key3(x) for x in pref}) == len(pref), "Duplicate template preference keys")
    require(all(not x["meaning_fidelity"] and not x["register_fit"] and not x["naturalness_1_to_5"] and not x["annotator_id"] for x in rating), "Ratings template contains filled annotations")
    require(all(not x["preferred_candidate_id"] and not x["annotator_id"] for x in pref), "Preference template contains filled annotations")
    require(all(x["family_id"] in {f"F{i:03d}" for i in range(1,25)} for x in rating + pref), "Pilot template includes out-of-scope family")

    targeted = read_csv("pilot/targeted_review_template.csv")
    require(len(targeted) == 6, f"Expected six targeted review rows; found {len(targeted)}")
    require({x["family_id"] for x in targeted} == target_ids, "Targeted review IDs disagree with issue register")
    require(all(not x["reviewer"] and not x["finding"] and not x["decision"] for x in targeted), "Targeted review template contains non-verified findings")

    md = (ROOT / "pilot/issues_log.md").read_text(encoding="utf-8")
    require(all(issue_id in md for issue_id in issue_ids), "Markdown issue log does not list every CSV issue")
    required = ["README.md", "docs/annotation_guide.md", "docs/data_schema.md", "validation_report.md"]
    require(all((ROOT/x).is_file() for x in required), "Missing supporting documentation")

    n_groups = Counter(group_ids)
    print("HindiPRAG release validation")
    print("  Families:",len(records),"| Candidates:",sum(len(r["candidates"]) for r in records))
    print("  Template groups:",len(n_groups),"| Groups reused:",sum(v>1 for v in n_groups.values()))
    print("  Open issues:",len(issues),"| Targeted review families:",len(target_ids))
    print("  Pilot families:",len(status),"| Blank prompt choices:",len(pref),"| Blank candidate ratings:",len(rating))
    print("  Preference labels populated: 0 (expected)")
    print("  SHA256 JSONL:",hashlib.sha256(jsonl.read_bytes()).hexdigest())
    if ERR:
        print(f"FAILED ({len(ERR)} checks):")
        for error in ERR:
            print(" -",error)
        return 1
    print("PASS: Structural and cross-file checks only; semantic review still pending.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

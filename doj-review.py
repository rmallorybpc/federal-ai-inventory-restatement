"""DOJ matcher calibration and manual review sheet.

Run from anywhere:
    python doj-review.py

Part 1, calibration:
  For each DOJ 2024 use case matched to 2025 by identifier, find the best
  2025 candidate by text similarity alone, ignoring identifiers. Report
  how often the best candidate is the true partner at each threshold.
  This is the error model for agencies without identifiers, such as HHS.

Part 2, review sheet:
  For each DOJ 2024 use case not matched by identifier, list the top 3
  2025 candidates from all DOJ 2025 rows. Writes a CSV to label by hand.

Outputs go to results/doj-pilot/. Keep that folder out of the public repo.
"""

import difflib
import glob
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "results" / "doj-pilot"

PURPOSE_24 = "What is the intended purpose and expected benefits of the AI?"
STAGE_24 = "Stage of Development"
THRESHOLDS = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
TOP_N = 3
STOP = {
    "the", "and", "for", "with", "that", "this", "from", "are", "use", "used",
    "ai", "data", "will", "can", "into", "its", "their", "which", "has", "have",
    "doj", "case", "system", "tool", "tools", "using", "information",
}


def norm(text):
    if pd.isna(text):
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def norm_id(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", "", str(value)).upper()


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", norm(text)) if len(w) > 2 and w not in STOP}


def name_sim(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load():
    doj24_path = glob.glob(str(ROOT / "agency-files" / "doj" / "FINAL_2024*"))[0]
    doj24 = pd.read_csv(doj24_path, encoding="utf-8-sig")
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig")
    doj25 = ind[ind["agency"].astype(str).str.strip().str.upper() == "DOJ"].copy()
    doj25 = doj25.reset_index(drop=True)

    doj24["nid"] = doj24["Use Case ID"].map(norm_id)
    doj24["sname"] = doj24["Use Case Name"].map(squash)
    doj24["words"] = (doj24["Use Case Name"].fillna("").astype(str) + " " + doj24[PURPOSE_24].fillna("").astype(str)).map(words)

    doj25["nid"] = doj25["id"].map(norm_id)
    doj25["sname"] = doj25["use_case_name"].map(squash)
    doj25["text"] = (
        doj25["use_case_name"].fillna("").astype(str) + " "
        + doj25["problem_solved"].fillna("").astype(str) + " "
        + doj25["benefits"].fillna("").astype(str)
    )
    doj25["words"] = doj25["text"].map(words)
    doj25["stext"] = doj25["text"].map(squash)
    return doj24, doj25


def score_all(row24, doj25):
    """Score one 2024 row against every 2025 row."""
    out = []
    for i, c in doj25.iterrows():
        ns = name_sim(row24["sname"], c["sname"])
        dj = jaccard(row24["words"], c["words"])
        contained = len(row24["sname"]) >= 5 and row24["sname"] in c["stext"]
        out.append((i, ns, dj, contained, max(ns, dj)))
    out.sort(key=lambda t: -t[4])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doj24, doj25 = load()

    ids25 = set(doj25["nid"]) - {""}
    matched24 = doj24[doj24["nid"].isin(ids25)]
    unmatched24 = doj24[~doj24["nid"].isin(ids25) & (doj24["sname"] != "")]

    # Part 1: calibration
    print("=" * 70)
    print("1. Calibration on identifier-matched pairs")
    print("=" * 70)
    rows = []
    for _, r in matched24.iterrows():
        ranked = score_all(r, doj25)
        best_i, ns, dj, contained, best = ranked[0]
        rows.append({
            "nid": r["nid"],
            "best_score": best,
            "top_is_true": doj25.loc[best_i, "nid"] == r["nid"],
            "true_in_top3": r["nid"] in {doj25.loc[i, "nid"] for i, *_ in ranked[:TOP_N]},
        })
    cal = pd.DataFrame(rows)
    n = len(cal)
    print(f"pairs: {n}")
    print(f"top candidate is the true partner, any score: {cal['top_is_true'].mean():.1%}")
    print(f"true partner in top {TOP_N}, any score: {cal['true_in_top3'].mean():.1%}")
    print()
    print("threshold  found_true  wrong_match  no_match")
    for t in THRESHOLDS:
        above = cal["best_score"] >= t
        found = (above & cal["top_is_true"]).sum()
        wrong = (above & ~cal["top_is_true"]).sum()
        none = (~above).sum()
        print(f"  {t:.1f}      {found / n:6.1%}      {wrong / n:6.1%}     {none / n:6.1%}")
    print()
    print("found_true: matcher pairs it correctly.")
    print("wrong_match: matcher pairs it with the wrong 2025 entry.")
    print("no_match: matcher finds nothing above the threshold, so a real")
    print("continuation would be counted as one disappearance and one new entry.")
    cal.to_csv(OUT / "calibration.csv", index=False)

    # Part 2: review sheet
    print()
    print("=" * 70)
    print("2. Review sheet for 2024 use cases not matched by identifier")
    print("=" * 70)
    sheet = []
    for _, r in unmatched24.iterrows():
        ranked = score_all(r, doj25)
        rec = {
            "id_2024": r["Use Case ID"],
            "name_2024": r["Use Case Name"],
            "stage_2024": norm(r[STAGE_24]).split(" - ")[0],
            "purpose_2024": str(r[PURPOSE_24])[:300],
        }
        for k, (i, ns, dj, contained, best) in enumerate(ranked[:TOP_N], start=1):
            c = doj25.loc[i]
            rec[f"c{k}_id"] = c["id"]
            rec[f"c{k}_name"] = c["use_case_name"]
            rec[f"c{k}_stage"] = c["development_stage"]
            rec[f"c{k}_continues_2024_id"] = c["nid"] in set(doj24["nid"])
            rec[f"c{k}_score"] = round(best, 2)
            rec[f"c{k}_name_in_text"] = contained
            rec[f"c{k}_problem"] = str(c["problem_solved"])[:300]
        rec["label"] = ""
        rec["matched_2025_id"] = ""
        rec["notes"] = ""
        sheet.append(rec)
    review = pd.DataFrame(sheet)
    path = OUT / "review-2024-unmatched.csv"
    review.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"rows to review: {len(review)}")
    print(f"top candidate already continues another 2024 id: {review['c1_continues_2024_id'].sum()}")
    print(f"2024 name appears inside a candidate's text: {review[[f'c{k}_name_in_text' for k in range(1, TOP_N + 1)]].any(axis=1).sum()}")
    print()
    print(f"review sheet written to {path}")


if __name__ == "__main__":
    main()

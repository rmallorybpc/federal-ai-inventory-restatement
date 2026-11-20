"""Score the VA blind test against VA's identifiers.

Run from anywhere:
    python va-blind-score.py

Reads from results/va-pilot/:
  review-va-blind-analyst.csv   the analyst's labels
  review-va-blind-ai.csv        the AI-assisted rater's labels
  va-blind-truth.csv            the answers

Labels: match (with matched_key), gone, unsure.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "va-pilot"


def clean(v):
    return "" if pd.isna(v) else str(v).strip()


def outcome(label, key, true_key):
    label, key = clean(label).lower(), clean(key).upper()
    if label not in {"match", "gone", "unsure"}:
        return "unlabeled"
    if true_key:
        if label == "match":
            return "found" if key == true_key else "wrong partner"
        return "false gone" if label == "gone" else "unsure"
    if label == "gone":
        return "correct gone"
    return "false match" if label == "match" else "unsure"


def score(name, sheet, truth):
    d = sheet.merge(truth, on="id_2024", how="left").fillna("")
    d["outcome"] = [outcome(l, k, t) for l, k, t in zip(d["label"], d["matched_key"], d["true_key"])]
    has = d[d["true_key"] != ""]
    none = d[d["true_key"] == ""]
    print(f"--- {name}")
    print(f"rows with a true 2025 partner: {len(has)}")
    print(has["outcome"].value_counts().to_string())
    if len(has):
        print(f"  true continuations found: {(has['outcome'] == 'found').mean():.0%}")
        print(f"  wrongly labeled gone:     {(has['outcome'] == 'false gone').mean():.0%}")
    print(f"rows with no 2025 partner: {len(none)}")
    if len(none):
        print(none["outcome"].value_counts().to_string())
    said_gone = d[d["label"].map(lambda v: clean(v).lower()) == "gone"]
    if len(said_gone):
        wrong = (said_gone["true_key"] != "").sum()
        print(f"of {len(said_gone)} rows labeled gone, {wrong} had a real partner ({wrong / len(said_gone):.0%})")
    print()
    return d


def kappa(a, b):
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((list(a).count(c) / n) * (list(b).count(c) / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    truth = pd.read_csv(OUT / "va-blind-truth.csv", encoding="utf-8-sig", dtype=str).fillna("")
    an = pd.read_csv(OUT / "review-va-blind-analyst.csv", encoding="utf-8-sig", dtype=str).fillna("")
    ai = pd.read_csv(OUT / "review-va-blind-ai.csv", encoding="utf-8-sig", dtype=str).fillna("")

    da = score("analyst", an, truth)
    db = score("AI-assisted rater", ai, truth)

    # Rows the AI rater had already seen in earlier output are not blind.
    seen = set(ai[ai["notes"].str.startswith("SEEN")]["id_2024"])
    if seen:
        print(f"=== excluding {len(seen)} rows whose answers appeared in earlier output ===")
        print()
        score("analyst, unseen rows", an[~an["id_2024"].isin(seen)], truth)
        score("AI-assisted rater, unseen rows", ai[~ai["id_2024"].isin(seen)], truth)

    m = da[["id_2024", "label", "matched_key"]].merge(
        db[["id_2024", "label", "matched_key"]], on="id_2024", suffixes=("_an", "_ai"))
    la = m["label_an"].map(lambda v: clean(v).lower())
    lb = m["label_ai"].map(lambda v: clean(v).lower())
    po, k = kappa(list(la), list(lb))
    same_key = ((la == "match") & (lb == "match")
                & (m["matched_key_an"].str.upper() == m["matched_key_ai"].str.upper())).sum()
    both_match = ((la == "match") & (lb == "match")).sum()
    print("--- agreement between the two raters")
    print(f"same label: {po:.0%}   Cohen's kappa: {k:.2f}")
    print(f"both said match: {both_match}   and chose the same entry: {same_key}")


if __name__ == "__main__":
    main()

"""Agency matching, 2024 to 2025. Same tiers as the pilots.

Run from anywhere, with the OMB agency code and a one-letter key prefix:
    python agency-match.py NASA N

Keys look like N24-001 and N25-001.

Tiers:
  1 exact name (squashed)
  2 disclosed rename (2025 text says "previously")
  3 mutual best score 0.6 or higher
  4 manual review (top 3 candidates listed)

Writes to results/<agency>/ (kept out of the public repo):
  review-<agency>.csv     one row per 2024 entry, with blank label columns
  <agency>-2025-all.csv   every 2025 entry, for the full-list search (spec 6a)
Does not overwrite the review file if it exists, so labels are safe.
"""

import difflib
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
if len(sys.argv) < 3:
    sys.exit("usage: python agency-match.py AGENCY PREFIX   for example: python agency-match.py NASA N")
AG = sys.argv[1].upper()
PX = sys.argv[2].upper()
OUT = ROOT / "results" / AG.lower()


def norm(text):
    if pd.isna(text):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def score(a, b):
    ratio = difflib.SequenceMatcher(None, squash(a), squash(b)).ratio()
    wa, wb = set(norm(a).split()), set(norm(b).split())
    jac = len(wa & wb) / len(wa | wb) if wa | wb else 0
    return round(max(ratio, jac), 2)


def find_col(cols, *words):
    for w in words:
        for c in cols:
            if w in c.lower():
                return c
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    review_path = OUT / f"review-{AG.lower()}.csv"
    if review_path.exists():
        sys.exit(f"{review_path} exists. Rename it first if you want a fresh copy.")

    hdr = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str, nrows=0)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = hdr.columns
    old = v2[v2["3_abr"].fillna("").str.strip().str.upper() == AG].reset_index(drop=True)
    stage24 = find_col(old.columns, "stage")
    purp24 = find_col(old.columns, "purpose")
    bur24 = find_col(old.columns, "bureau", "component")

    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    new = ind[ind["agency"].fillna("").str.strip().str.upper() == AG].reset_index(drop=True)
    purp25 = find_col(new.columns, "purpose", "problem")

    old["key"] = [f"{PX}24-{i:03d}" for i in range(1, len(old) + 1)]
    new["key"] = [f"{PX}25-{i:03d}" for i in range(1, len(new) + 1)]
    on = old["2_use_case_name"].fillna("").tolist()
    nn = new["use_case_name"].fillna("").tolist()

    s = [[score(a, b) for b in nn] for a in on]
    best_new = [max(range(len(nn)), key=lambda j: s[i][j]) for i in range(len(on))]
    best_old = [max(range(len(on)), key=lambda i: s[i][j]) for j in range(len(nn))]

    text25 = new.fillna("").astype(str).agg(" ".join, axis=1).map(norm)
    sq_new = {squash(n): j for j, n in enumerate(nn)}

    rows = []
    for i, name in enumerate(on):
        tier, pick = 4, None
        if squash(name) in sq_new and squash(name):
            tier, pick = 1, sq_new[squash(name)]
        else:
            hits = [j for j in range(len(nn)) if "previously" in text25[j] and squash(name) in squash(text25[j])]
            if hits:
                tier, pick = 2, hits[0]
            elif s[i][best_new[i]] >= 0.6 and best_old[best_new[i]] == i:
                tier, pick = 3, best_new[i]
        top = sorted(range(len(nn)), key=lambda j: -s[i][j])[:3]
        row = {
            "key_2024": old.at[i, "key"],
            "name_2024": name,
            "bureau_2024": old.at[i, bur24] if bur24 else "",
            "stage_2024": old.at[i, stage24] if stage24 else "",
            "purpose_2024": str(old.at[i, purp24])[:300] if purp24 else "",
            "tier": tier,
            "proposed_2025_key": new.at[pick, "key"] if pick is not None else "",
            "proposed_2025_name": nn[pick] if pick is not None else "",
            "score": s[i][pick] if pick is not None else "",
        }
        for k, j in enumerate(top, 1):
            row[f"cand{k}"] = f"{new.at[j, 'key']} | {s[i][j]} | {nn[j][:80]}"
        row.update({"label": "", "matched_2025_key": "", "notes": ""})
        rows.append(row)

    rev = pd.DataFrame(rows)
    rev.to_csv(review_path, index=False, encoding="utf-8-sig")

    keep = ["key", "use_case_name", "bureau", "topic_area", "development_stage"] + ([purp25] if purp25 else [])
    new[[c for c in keep if c in new.columns]].to_csv(OUT / f"{AG.lower()}-2025-all.csv", index=False, encoding="utf-8-sig")

    print(f"{AG} 2024: {len(on)}   2025: {len(nn)}")
    tagged = new["use_case_name"].fillna("").str.contains(r"inv\s*#|previously", case=False).sum()
    retired25 = new["development_stage"].fillna("").str.lower().str.startswith("retired").sum()
    print(f"2025 names citing a prior inventory: {tagged}   2025 retired: {retired25}")
    print(f"columns found: stage={stage24}  purpose={purp24}  bureau={bur24}  purpose_2025={purp25}")
    print(rev["tier"].value_counts().sort_index().rename("rows by tier").to_string())
    if stage24:
        print(f"retired in 2024 file: {old[stage24].fillna('').str.lower().str.startswith('retired').sum()}")
    print(f"written: {review_path}")


if __name__ == "__main__":
    main()

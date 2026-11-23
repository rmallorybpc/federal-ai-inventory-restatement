"""Test the 2024 inventory IDs that DOI wrote into its 2025 names.

Run from anywhere:
    python doi-ids.py

Many DOI 2025 names end with a tag such as
  [2024 INV#WO0000000110323]  or  [2024 INV#DOI-58]
This script pulls those IDs and looks for each one in the DOI 2024 rows
(any field). It then compares the ID links to the proposals in
results/doi/review-doi.csv.

Writes results/doi/doi-id-links.csv. Does not touch review-doi.csv.
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "results" / "doi"
AG = "DOI"

TAG = re.compile(r"\[([^\]]*inv[^\]]*)\]", re.I)
ONE_ID = re.compile(r"(WO\d+|DOI-\d+)", re.I)


def main():
    hdr = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str, nrows=0)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = hdr.columns
    old = v2[v2["3_abr"].fillna("").str.strip().str.upper() == AG].reset_index(drop=True)
    old["key"] = [f"D24-{i:03d}" for i in range(1, len(old) + 1)]

    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    new = ind[ind["agency"].fillna("").str.strip().str.upper() == AG].reset_index(drop=True)
    new["key"] = [f"D25-{i:03d}" for i in range(1, len(new) + 1)]

    # where do the IDs live in 2024
    cells = old.drop(columns="key").fillna("").astype(str)
    col_hits = {c: cells[c].str.contains(r"WO\d{6,}|DOI-\d+", case=False, regex=True).sum() for c in cells.columns}
    col_hits = {c: n for c, n in col_hits.items() if n}
    print("2024 columns holding IDs:", col_hits if col_hits else "none found")

    links = []
    tagged = 0
    for _, r in new.iterrows():
        name = str(r["use_case_name"]) if pd.notna(r["use_case_name"]) else ""
        ids = [i.upper() for t in TAG.findall(name) for i in ONE_ID.findall(t)]
        if not ids:
            continue
        tagged += 1
        for i in ids:
            pat = re.compile(rf"(?<![A-Z0-9-]){re.escape(i)}(?!\d)", re.I)
            hits = old[cells.apply(lambda row: bool(pat.search(" ".join(row))), axis=1)]
            if hits.empty:
                links.append({"key_2025": r["key"], "name_2025": name, "tag_id": i, "key_2024": "", "name_2024": ""})
            for _, h in hits.iterrows():
                links.append({"key_2025": r["key"], "name_2025": name, "tag_id": i,
                              "key_2024": h["key"], "name_2024": h["2_use_case_name"]})

    lk = pd.DataFrame(links)
    lk.to_csv(OUT / "doi-id-links.csv", index=False, encoding="utf-8-sig")
    found = lk[lk["key_2024"] != ""]
    print(f"2025 entries with a 2024 tag: {tagged} of {len(new)}")
    print(f"tag IDs: {lk['tag_id'].nunique()}   found in 2024: {found['tag_id'].nunique()}   not found: {lk[lk['key_2024'] == '']['tag_id'].nunique()}")
    print(f"2024 entries linked by ID: {found['key_2024'].nunique()} of {len(old)}")
    multi = found.groupby("key_2025")["key_2024"].nunique()
    print(f"2025 entries linked to 2 or more 2024 entries: {(multi > 1).sum()}")

    rev_path = OUT / "review-doi.csv"
    if rev_path.exists():
        rev = pd.read_csv(rev_path, dtype=str, encoding="utf-8-sig").fillna("")
        by_old = found.groupby("key_2024")["key_2025"].apply(set)
        agree = disagree = id_only = 0
        rows = []
        for _, r in rev.iterrows():
            ids = by_old.get(r["key_2024"], set())
            if not ids:
                continue
            if r["proposed_2025_key"] in ids:
                agree += 1
            elif r["proposed_2025_key"]:
                disagree += 1
                rows.append((r["key_2024"], r["proposed_2025_key"], ",".join(sorted(ids))))
            else:
                id_only += 1
        print()
        print(f"vs name proposals: agree {agree}   disagree {disagree}   ID link where names found none {id_only}")
        for k, p, i in rows:
            print(f"  {k}: name proposal {p}, ID link {i}")
    print(f"written: {OUT / 'doi-id-links.csv'}")


if __name__ == "__main__":
    main()

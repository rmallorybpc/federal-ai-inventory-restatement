"""Check whether an agency's commercial tools from 2024 appear in the 2025 commercial file.

Run from anywhere, with the agency code, a word in its full name, and the
product words to search for:
    python cots-check.py DOE energy crowdstrike coupa

Prints matches only. Writes nothing.
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
if len(sys.argv) < 4:
    sys.exit("usage: python cots-check.py AGENCY NAMEWORD TERM [TERM ...]")
AG = sys.argv[1].upper()
NAMEWORD = sys.argv[2].lower()
TERMS = {w: [w.lower()] for w in sys.argv[3:]}


def main():
    files = [p for p in P25.glob("*.csv") if re.search(r"commercial|cots", p.name, re.I)]
    print("2025 files checked:", [p.name for p in files] or "none found")
    print("all CSV files in the folder:", [p.name for p in P25.glob("*.csv")])
    for p in files:
        df = pd.read_csv(p, encoding="utf-8-sig", dtype=str).fillna("")
        ag_col = next((c for c in df.columns if "agency" in c.lower()), None)
        if ag_col is None:
            print(f"{p.name}: no agency column. Columns: {list(df.columns)}")
            continue
        ag = df[ag_col].str.strip()
        d = df[(ag.str.upper() == AG) | ag.str.contains(NAMEWORD, case=False)]
        print(f"\n{p.name}: {len(d)} agency rows. Columns: {list(df.columns)}")
        if d.empty:
            print("agency values in this file:", sorted(ag.unique())[:60])
            continue
        text = d.astype(str).agg(" | ".join, axis=1).str.lower()
        for label, words in TERMS.items():
            hits = d[text.str.contains("|".join(re.escape(w) for w in words), regex=True)]
            print(f"\n  {label}: {len(hits)} rows")
            for _, r in hits.iterrows():
                print("    ", " | ".join(v[:60] for v in r.values if v)[:220])


if __name__ == "__main__":
    main()

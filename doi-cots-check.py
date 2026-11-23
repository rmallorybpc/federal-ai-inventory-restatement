"""Check whether DOI's commercial tools from 2024 moved to the 2025 commercial file.

Run from anywhere:
    python doi-cots-check.py

Looks in the 2025 data folder for any CSV whose name contains
"commercial" or "cots", keeps DOI rows, and searches every field for the
product and tool words below. Prints matches only. Writes nothing.
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
AG = "DOI"

TERMS = {
    "D24-001 to 003 DOIChatGPT": ["chatgpt", "openai", "govchat", "gpt", "chat"],
    "D24-005 Adobe Firefly": ["adobe", "firefly", "photoshop"],
    "D24-014 NPS acquisition drafting": ["procure", "acquisition", "contract"],
    "D24-015 CaseGuard": ["caseguard", "redact"],
    "D24-168 Articulate": ["articulate", "text to speech", "text-to-speech"],
}


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
        d = df[(ag.str.upper() == AG) | ag.str.contains("interior", case=False)]
        print(f"\n{p.name}: {len(d)} DOI rows. Columns: {list(df.columns)}")
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

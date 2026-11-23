"""Check why DOI has so few 2024 name matches.

Run from anywhere:
    python doi-check.py

Prints 10 DOI use case names from each year, then counts how many 2024
DOI names have a likely 2025 match (score 0.6 or higher, same scoring
as the pilots). Counts and names only. Writes nothing.
"""

import difflib
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"


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
    return max(ratio, jac)


def main():
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str, nrows=0)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)

    old = v2[v2["3_abr"].fillna("").str.strip().str.upper() == "DOI"]["2_use_case_name"].dropna().tolist()
    new = ind[ind["agency"].fillna("").str.strip().str.upper() == "DOI"]["use_case_name"].dropna().tolist()
    print(f"DOI 2024: {len(old)}   DOI 2025: {len(new)}")
    print()
    print("2024 names (first 10):")
    for n in old[:10]:
        print("  ", n[:90])
    print()
    print("2025 names (first 10):")
    for n in new[:10]:
        print("  ", n[:90])
    print()

    exact = sum(1 for o in old if squash(o) in {squash(n) for n in new})
    best = [max((score(o, n) for n in new), default=0) for o in old]
    print(f"exact name matches: {exact}")
    print(f"best score 0.6 or higher: {sum(b >= 0.6 for b in best)}")
    print(f"best score 0.4 to 0.6: {sum(0.4 <= b < 0.6 for b in best)}")
    print(f"best score under 0.4: {sum(b < 0.4 for b in best)}")


if __name__ == "__main__":
    main()

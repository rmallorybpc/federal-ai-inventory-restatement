"""Research and development scope check for NASA and DOE.

Run from anywhere:
    python scope-check.py

Question: did 2025 growth at NASA and DOE come from new use, or from
research uses returning to the inventory after the 2024 definition
excluded them?

For each agency:
  1. Counts in the 2023, 2024, and 2025 inventories.
  2. 2025 entries that match a 2023 entry (by normalized id or exact
     name) but no 2024 entry. These are candidates for returned scope.
  3. 2025 stage for each group.

Ids are normalized: uppercase, spaces removed, all dash types unified,
leading zeros dropped from the number.
"""

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
    s = unicodedata.normalize("NFKC", str(text))
    return re.sub(r"\s+", " ", s).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def norm_id(v):
    if pd.isna(v):
        return ""
    s = unicodedata.normalize("NFKC", str(v)).upper()
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"\s+", "", s)
    return re.sub(r"(?<=-)0+(?=\d)", "", s)


def stage_short(v):
    s = re.sub(r"^[a-e]\)\s*", "", norm(v))
    s = re.split(r"\s+[-–]\s+", s)[0]
    return s or "(blank)"


def main():
    d23 = pd.read_csv(P24 / "2023_consolidated_ai_inventory_raw.csv", encoding="cp1252",
                      encoding_errors="replace", dtype=str)
    print("2023 rows by department code:")
    print(d23["Department_Code"].fillna("(blank)").value_counts().to_string())

    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)

    for ag in ["NASA", "DOE"]:
        print()
        print("=" * 70)
        print(ag)
        print("=" * 70)
        a23 = d23[d23["Department_Code"].fillna("").str.upper().str.strip() == ag]
        a24 = v2[v2["3_abr"].fillna("").str.upper().str.strip() == ag]
        a25 = ind[ind["agency"].fillna("").str.upper().str.strip() == ag].copy()
        print(f"counts: 2023 {len(a23)}   2024 {len(a24)}   2025 {len(a25)}")
        print(f"2023 sample ids: {a23['Use_Case_ID'].head(4).tolist()}")

        ids23 = set(a23["Use_Case_ID"].map(norm_id)) - {""}
        names23 = set(a23["Title"].map(squash)) - {""}
        names24 = set(a24["2_use_case_name"].map(squash)) - {""}

        a25["nid"] = a25["id"].map(norm_id)
        a25["sname"] = a25["use_case_name"].map(squash)
        a25["in24"] = a25["sname"].isin(names24)
        a25["in23"] = a25["nid"].isin(ids23) | a25["sname"].isin(names23)
        a25["stage_s"] = a25["development_stage"].map(stage_short)

        def group(r):
            if r["in24"]:
                return "in 2024"
            if r["in23"]:
                return "in 2023 only"
            return "neither"

        a25["group"] = a25.apply(group, axis=1)
        print(f"2025 ids also in 2023 ids: {a25['nid'].isin(ids23).sum()}")
        print("2025 entries by earlier appearance (exact name or id):")
        print(a25["group"].value_counts().to_string())
        print()
        print("2025 stage by group:")
        print(pd.crosstab(a25["group"], a25["stage_s"]).to_string())
        print()
        print("examples, in 2023 only:")
        for n in a25[a25["group"] == "in 2023 only"]["use_case_name"].head(8):
            print(f"  {str(n)[:90]}")
        print("examples, neither:")
        for n in a25[a25["group"] == "neither"]["use_case_name"].head(8):
            print(f"  {str(n)[:90]}")


if __name__ == "__main__":
    main()

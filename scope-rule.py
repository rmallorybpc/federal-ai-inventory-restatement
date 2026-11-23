"""Apply the field rule for research and development scope.

Run from anywhere:
    python scope-rule.py

Rule, from definition spec section 9:
  An entry counts as research when its topic area is Science and its
  stage is not Deployed.

Applied to every agency's 2025 entries, with a focus on entries that
have no 2023 or 2024 name match at NASA and DOE. Also counts entries
whose benefits text says the AI was automatically integrated without an
identified benefit.

Counts only. Writes results/scope/scope-rule.csv with per agency rows.
Keep results/ out of the public repo.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "results" / "scope"


def norm(text):
    if pd.isna(text):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def stage_short(v):
    s = re.sub(r"^[a-e]\)\s*", "", norm(v))
    return re.split(r"\s+[-–]\s+", s)[0] or "(blank)"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    ind["ag"] = ind["agency"].fillna("").str.upper().str.strip()
    ind["stage_s"] = ind["development_stage"].map(stage_short)
    ind["science"] = ind["topic_area"].map(norm) == "science"
    ind["research"] = ind["science"] & (ind["stage_s"] != "deployed")
    ind["embedded"] = ind["benefits"].fillna("").str.contains("automatically integrated", case=False)

    print("topic area values containing 'science':")
    print(ind[ind["topic_area"].map(norm).str.contains("scien")]["topic_area"].value_counts().to_string())
    print()

    by = ind.groupby("ag").agg(n_2025=("ag", "size"), research=("research", "sum"),
                               science_any_stage=("science", "sum"), embedded=("embedded", "sum"))
    by["research_share"] = (by["research"] / by["n_2025"]).round(2)
    by = by.sort_values("research", ascending=False)
    by.to_csv(OUT / "scope-rule.csv")
    print("2025 entries meeting the rule, by agency (top 15):")
    print(by.head(15).to_string())
    print()
    print(f"all agencies: {by['research'].sum()} of {by['n_2025'].sum()} meet the rule")
    print(f"embedded, no identified benefit: {by['embedded'].sum()}")

    # NASA and DOE entries with no prior record
    d23 = pd.read_csv(P24 / "2023_consolidated_ai_inventory_raw.csv", encoding="cp1252",
                      encoding_errors="replace", dtype=str)
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    print()
    for ag in ["NASA", "DOE", "DOI", "USDA", "HHS"]:
        prior = set(d23[d23["Department_Code"].fillna("").str.upper().str.strip() == ag]["Title"].map(squash)) \
            | set(v2[v2["3_abr"].fillna("").str.upper().str.strip() == ag]["2_use_case_name"].map(squash))
        a = ind[ind["ag"] == ag]
        new = a[~a["use_case_name"].map(squash).isin(prior)]
        print(f"{ag}: no prior record {len(new)}   meet rule {new['research'].sum()}"
              f"   science but deployed {(new['science'] & ~new['research']).sum()}")
    print()
    print(f"written: {OUT / 'scope-rule.csv'}")


if __name__ == "__main__":
    main()

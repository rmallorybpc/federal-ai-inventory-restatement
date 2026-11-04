"""Inspect value distributions in the fields the crosswalk depends on.

Run from anywhere:
    python inspect-fields.py

Paths resolve from this script's folder, so the terminal location
does not matter. The script expects the OMB clones in a sources
folder next to it.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"


def load():
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8")
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252")
    # The two 2024 files share a layout. Apply the coded names to v2.
    v2.columns = v1.columns
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig")
    cots = pd.read_csv(P25 / "2025_consolidated_COTS_AI_use_cases.csv", encoding="utf-8-sig")
    return v1, v2, ind, cots


def counts(title, series):
    print(f"== {title}")
    print(series.fillna("(blank)").value_counts().to_string())
    print()


def main():
    v1, v2, ind, cots = load()

    print("#### 2024 stage and commercial flag (2,133 file)")
    print()
    counts("2024 v2: 16_dev_stage", v2["16_dev_stage"])
    counts("2024 v2: 10_commercial_ai", v2["10_commercial_ai"])

    print("#### 2025 individually reported")
    print()
    counts("2025: development_stage", ind["development_stage"])
    counts("2025: classification", ind["classification"])
    counts("2025: is_withheld", ind["is_withheld"])

    print("== 2025: id coverage by agency (top 15 by rows)")
    cov = (
        ind.assign(has_id=ind["id"].notna() & (ind["id"].astype(str).str.strip() != ""))
        .groupby("agency")
        .agg(rows=("id", "size"), with_id=("has_id", "sum"))
        .sort_values("rows", ascending=False)
    )
    print(cov.head(15).to_string())
    print()

    print("== 2025: sample ids for DOJ")
    doj = ind[ind["agency"].astype(str).str.upper() == "DOJ"]
    print(doj["id"].head(10).to_string())
    print(f"DOJ rows: {len(doj)}")
    print()

    print("#### 2025 COTS grid")
    print()
    counts("COTS: AI Use Case categories", cots["AI Use Case"])
    counts("COTS: Agency Use (Y/N)?", cots["Agency Use (Y/N)?"])


if __name__ == "__main__":
    main()

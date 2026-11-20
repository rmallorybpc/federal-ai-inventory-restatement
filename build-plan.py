"""Draft the agency run order for the full build.

Run from anywhere:
    python build-plan.py

For every agency in either year's OMB file, reports the 2024 and 2025
counts and how many 2025 rows carry an id. Sorts agencies into tiers:

  done     DOJ, HHS, VA, completed in the pilot
  tier 1   25 or more use cases in 2025, ids on every 2025 row
  tier 2   25 or more use cases in 2025, ids missing on some or all rows
  tier 3   fewer than 25 use cases in 2025, batched together

Within each tier, larger agencies come first, so coverage builds fastest.
Writes data/build-plan.csv. Counts only, all from OMB's public files.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "data" / "build-plan.csv"
DONE = {"DOJ", "HHS", "VA"}
LARGE = 25


def main():
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)

    a24 = v2["3_abr"].fillna("").str.strip().str.upper()
    a25 = ind["agency"].fillna("").str.strip().str.upper()
    has_id = ind["id"].fillna("").str.strip() != ""

    plan = pd.DataFrame({
        "n_2024": a24.value_counts(),
        "n_2025": a25.value_counts(),
        "ids_2025": has_id.groupby(a25).sum(),
    }).fillna(0).astype(int)
    plan.index.name = "agency"
    plan = plan[plan.index != ""]

    def tier(r):
        if r.name in DONE:
            return "done"
        if r["n_2025"] >= LARGE:
            return "tier 1" if r["ids_2025"] == r["n_2025"] else "tier 2"
        return "tier 3"

    plan["tier"] = plan.apply(tier, axis=1)
    plan["id_coverage"] = (plan["ids_2025"] / plan["n_2025"].where(plan["n_2025"] > 0)).round(2)
    plan = plan.sort_values(["tier", "n_2025"], ascending=[True, False])
    plan["cum_2025"] = plan["n_2025"].cumsum()
    plan["cum_share"] = (plan["cum_2025"] / plan["n_2025"].sum()).round(3)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    plan.to_csv(OUT)

    pd.set_option("display.width", 140)
    print(plan.to_string())
    print()
    print("totals by tier:")
    t = plan.groupby("tier")[["n_2024", "n_2025"]].sum()
    t["agencies"] = plan.groupby("tier").size()
    print(t.to_string())
    print()
    only24 = plan[(plan["n_2024"] > 0) & (plan["n_2025"] == 0)].index.tolist()
    only25 = plan[(plan["n_2024"] == 0) & (plan["n_2025"] > 0)].index.tolist()
    print(f"in 2024 only: {only24}")
    print(f"in 2025 only: {only25}")
    print("Check these two lists for the same agency under different abbreviations.")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()

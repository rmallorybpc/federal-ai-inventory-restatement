"""Recount the research scope component using the matched review files.

Run from anywhere:
    python scope-pool.py

For each agency below, the pool is its active 2025 entries (stage not
Retired) that no reviewed 2024 entry links to. Links come from
results/<agency>/review-<agency>.csv, labels continues, renamed, merged,
retired, cots. Agencies without a review file fall back to exact name
match against 2023 and 2024, as in scope-rule.py.

Rule (spec 1.5): topic area Science and stage not Deployed.
Also counts pool entries whose name cites a prior inventory number.

Counts only. Writes results/scope/scope-pool.csv.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
RES = ROOT / "results"
AGENCIES = {"NASA": "N", "DOE": "E", "DOI": "D", "USDA": "U", "HHS": "H"}
LINK = {"continues", "renamed", "merged", "retired", "cots"}
BASE_2024 = 2133
TOTAL_2025 = 3611


def norm(text):
    if pd.isna(text):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def main():
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    ind["ag"] = ind["agency"].fillna("").str.strip().str.upper()
    d23 = pd.read_csv(P24 / "2023_consolidated_ai_inventory_raw.csv", encoding="cp1252",
                      encoding_errors="replace", dtype=str)
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str, nrows=0)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns

    rows = []
    for ag, px in AGENCIES.items():
        new = ind[ind["ag"] == ag].reset_index(drop=True)
        new["key"] = [f"{px}25-{i:03d}" for i in range(1, len(new) + 1)]
        stage = new["development_stage"].fillna("").str.strip().str.lower()
        active = new[~stage.str.startswith("retired")]
        rev_path = RES / ag.lower() / f"review-{ag.lower()}.csv"
        if rev_path.exists():
            rev = pd.read_csv(rev_path, dtype=str, encoding="utf-8-sig").fillna("")
            linked = set(rev[rev["label"].isin(LINK)]["matched_2025_key"])
            pool = active[~active["key"].isin(linked)]
            basis = "review file"
            unsure = int((rev["label"] == "unsure").sum())
        else:
            prior = set(d23[d23["Department_Code"].fillna("").str.upper().str.strip() == ag]["Title"].map(squash)) \
                | set(v2[v2["3_abr"].fillna("").str.upper().str.strip() == ag]["2_use_case_name"].map(squash))
            pool = active[~active["use_case_name"].map(squash).isin(prior)]
            basis = "exact name, 2023 and 2024"
            unsure = 0
        science = pool["topic_area"].map(norm) == "science"
        deployed = pool["development_stage"].fillna("").str.strip().str.lower() == "deployed"
        rule = science & ~deployed
        tagged = pool["use_case_name"].fillna("").str.contains(r"inv\s*#", case=False)
        rows.append({"agency": ag, "basis": basis, "active_2025": len(active), "pool": len(pool),
                     "meet_rule": int(rule.sum()), "meet_rule_tagged": int((rule & tagged).sum()),
                     "unsure_rows": unsure})

    out = pd.DataFrame(rows)
    (RES / "scope").mkdir(parents=True, exist_ok=True)
    out.to_csv(RES / "scope" / "scope-pool.csv", index=False)
    print(out.to_string(index=False))
    total = out["meet_rule"].sum()
    untagged = total - out["meet_rule_tagged"].sum()
    for label, n in [("rule, all", total), ("rule, tagged entries kept as prior", untagged)]:
        g = ((TOTAL_2025 - n) / BASE_2024 - 1) * 100
        print(f"{label}: {n} entries   growth on the 2024 ruler after removal: {g:.1f}%")
    print(f"published growth: {(TOTAL_2025 / BASE_2024 - 1) * 100:.1f}%")


if __name__ == "__main__":
    main()

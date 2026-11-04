"""DOJ pilot tally: final labels, agreement, COTS check, restatement.

Run from anywhere:
    python doj-tally.py

Reads results/doj-pilot/review-2024-labels.csv. For each row, the final
label is your entry in the label column when filled, otherwise the
proposed label. Rows where you filled a label are compared against the
proposal to measure agreement between the two raters.

Outputs go to the console only. Keep results/ out of the public repo.
"""

import glob
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
LABELS = ROOT / "results" / "doj-pilot" / "review-2024-labels.csv"
VALID = {"renamed", "merged", "retired", "gone", "cots", "scope", "unsure"}


def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def norm_id(value):
    return re.sub(r"\s+", "", clean(value)).upper()


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def growth(new, old):
    return f"{new / old - 1:.1%}"


def main():
    lab = pd.read_csv(LABELS, encoding="utf-8-sig", dtype=str)
    doj24 = pd.read_csv(glob.glob(str(ROOT / "agency-files" / "doj" / "FINAL_2024*"))[0], encoding="utf-8-sig")
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig")
    doj25 = ind[ind["agency"].astype(str).str.strip().str.upper() == "DOJ"].copy()
    cots = pd.read_csv(P25 / "2025_consolidated_COTS_AI_use_cases.csv", encoding="utf-8-sig")

    doj24["nid"] = doj24["Use Case ID"].map(norm_id)
    doj25["nid"] = doj25["id"].map(norm_id)
    ids25 = set(doj25["nid"]) - {""}

    # Final labels
    lab["mine"] = lab["label"].map(clean).str.lower()
    lab["prop"] = lab["proposed_label"].map(clean).str.lower()
    lab["final"] = lab.apply(lambda r: r["mine"] if r["mine"] else r["prop"], axis=1)
    lab["final_id"] = lab.apply(
        lambda r: norm_id(r["matched_2025_id"]) if r["mine"] else norm_id(r["proposed_2025_id"]), axis=1
    )

    section("1. Label source and agreement")
    filled = lab[lab["mine"] != ""]
    print(f"rows: {len(lab)}")
    print(f"labeled by you: {len(filled)}")
    print(f"using proposed label: {len(lab) - len(filled)}")
    bad = lab[~lab["final"].isin(VALID)]
    if len(bad):
        print(f"invalid labels, fix before trusting the tally: {len(bad)}")
        print(bad[["id_2024", "final"]].to_string(index=False))
    if len(filled):
        agree = (filled["mine"] == filled["prop"]).sum()
        print(f"agreement with proposal: {agree} of {len(filled)} ({agree / len(filled):.0%})")
        dis = filled[filled["mine"] != filled["prop"]]
        if len(dis):
            print("disagreements:")
            for _, r in dis.iterrows():
                print(f"  {r['id_2024']}  proposed {r['prop']}  yours {r['mine']}  |  {clean(r['name_2024'])[:50]}")

    section("2. Final label counts")
    print(lab["final"].value_counts().to_string())

    section("3. Matched 2025 ids that do not exist in DOJ 2025")
    needs_id = lab[lab["final"].isin({"renamed", "merged"})]
    missing = needs_id[~needs_id["final_id"].isin(ids25)]
    print(f"renamed or merged rows: {len(needs_id)}   missing or blank id: {len(missing)}")
    if len(missing):
        print(missing[["id_2024", "final", "final_id"]].to_string(index=False))

    section("4. COTS check")
    appx = next(c for c in doj24.columns if c.startswith("Is the AI use case found in Appendix B"))
    cots_rows = lab[lab["final"] == "cots"].merge(doj24[["nid", appx]], left_on="id_2024", right_on="nid", how="left")
    print("2024 Appendix B answer for rows labeled cots:")
    for _, r in cots_rows.iterrows():
        print(f"  {r['id_2024']}  {clean(r['name_2024'])[:35]:35}  |  {clean(r[appx])[:70]}")
    agency_col = cots["Agency"].astype(str)
    doj_cots = cots[agency_col.str.upper().eq("DOJ") | agency_col.str.lower().str.contains("justice")]
    print()
    print(f"DOJ rows in the 2025 COTS grid: {len(doj_cots)}  (agency value: {sorted(doj_cots['Agency'].unique())})")
    yes = doj_cots[doj_cots["Agency Use (Y/N)?"].astype(str).str.strip().str.upper() == "Y"]
    print(f"categories DOJ marked Y: {len(yes)}")
    for _, r in yes.iterrows():
        print(f"  {clean(r['AI Use Case'])[:75]}  |  {clean(r['Name of Commercial Product or Service Used'])[:40]}")

    section("5. DOJ 2024-side decomposition")
    real24 = doj24[doj24["Use Case Name"].map(clean) != ""]
    by_id = real24["nid"].isin(ids25).sum()
    c = lab["final"].value_counts().to_dict()
    merged = c.get("merged", 0)
    renamed = c.get("renamed", 0)
    rows = [
        ("continues by id", by_id),
        ("merged into another entry", merged),
        ("renamed under a new id", renamed),
        ("moved to COTS reporting", c.get("cots", 0)),
        ("dropped by scope or definition", c.get("scope", 0)),
        ("retired, disclosed", c.get("retired", 0)),
        ("gone, no counterpart", c.get("gone", 0)),
        ("unsure", c.get("unsure", 0)),
    ]
    total = 0
    for name, n in rows:
        print(f"  {name:30} {n:4}  ({n / len(real24):5.1%})")
        total += n
    print(f"  {'total':30} {total:4}  (2024 real use cases: {len(real24)})")
    cont = by_id + merged + renamed
    print()
    print(f"use cases that continue in some form: {cont} of {len(real24)} ({cont / len(real24):.1%})")
    print(f"persistence violations, renamed under a new id: {renamed}")
    dup = len(doj25) - doj25["nid"].nunique()
    print(f"duplicate rows in 2025: {dup}")
    print()
    print("n-count for the disappearance cell, DOJ only:")
    gone = c.get("gone", 0)
    print(f"  gone: {gone}   gone plus unsure: {gone + c.get('unsure', 0)}")

    section("6. DOJ restatement under each ruler, preliminary")
    old = len(real24)
    pub = len(doj25)
    a = pub - dup
    moved = merged + c.get("scope", 0) + c.get("cots", 0)
    r24_new = a + moved
    r25_old = old - moved
    print(f"  published, OMB counts:                {old} -> {pub}   growth {growth(pub, old)}")
    print(f"  duplicates removed:                   {old} -> {a}   growth {growth(a, old)}")
    print(f"  2024 ruler, 2025 restated:            {old} -> {r24_new}   growth {growth(r24_new, old)}")
    print(f"  2025 ruler, 2024 restated:            {r25_old} -> {a}   growth {growth(a, r25_old)}")
    print()
    print("2024 ruler: 2025 counted at 2024 granularity and scope. Merged,")
    print("scope and COTS rows are added back to the 2025 count.")
    print("2025 ruler: 2024 counted at 2025 granularity and scope. The same")
    print("rows are removed from the 2024 base.")
    print("Published growth mixes the two rulers. Unsure rows are in neither.")


if __name__ == "__main__":
    main()

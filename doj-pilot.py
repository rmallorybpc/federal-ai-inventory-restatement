"""DOJ identifier stability pilot.

Run from anywhere:
    python doj-pilot.py

Checks:
  1. DOJ 2024 identifiers: format, blanks, duplicates.
  2. Reconcile DOJ's own 2024 file (241) with OMB's 2024 v2 file (240).
  3. Match DOJ 2024 identifiers into OMB's 2025 file.
  4. Matched ids: name change, scored by similarity.
  5. Duplicate identifiers in 2025.
  6. DOJ 2024 retired use cases.
  7. 2024-only ids: renumbered, retired, blank, fuzzy candidate, unexplained.
  8. 2025-only ids by 2025 stage.
  9. Tentative 2024-side bucket tally.

Detail rows are written to results/doj-pilot/. Keep that folder out of
the public repo.
"""

import difflib
import glob
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "results" / "doj-pilot"
SHOW = 15

PURPOSE_24 = "What is the intended purpose and expected benefits of the AI?"
STAGE_24 = "Stage of Development"

# Similarity thresholds. Working values for the pilot, not locked.
COSMETIC = 0.80
PARTIAL = 0.50
CANDIDATE = 0.80


def norm(text):
    """Normalize text for comparison across files and encodings."""
    if pd.isna(text):
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def squash(text):
    """Letters and digits only. Makes 'CellHawk' equal 'Cell Hawk'."""
    return re.sub(r"[^a-z0-9]", "", norm(text))


def norm_id(value):
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", "", str(value)).upper()


def ratio(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def is_retired(stage):
    return norm(stage).startswith("retired")


def load():
    doj24_path = glob.glob(str(ROOT / "agency-files" / "doj" / "FINAL_2024*"))[0]
    doj24 = pd.read_csv(doj24_path, encoding="utf-8-sig")

    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8")
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252")
    v2.columns = v1.columns
    omb24 = v2[v2["3_abr"].astype(str).str.strip().str.upper() == "DOJ"].copy()

    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig")
    omb25 = ind[ind["agency"].astype(str).str.strip().str.upper() == "DOJ"].copy()

    return doj24, omb24, omb25


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    doj24, omb24, omb25 = load()

    doj24["nid"] = doj24["Use Case ID"].map(norm_id)
    doj24["nname"] = doj24["Use Case Name"].map(norm)
    doj24["sname"] = doj24["Use Case Name"].map(squash)
    doj24["ndesc"] = doj24[PURPOSE_24].map(norm)
    doj24["retired"] = doj24[STAGE_24].map(is_retired)

    omb24["nname"] = omb24["2_use_case_name"].map(norm)

    omb25["nid"] = omb25["id"].map(norm_id)
    omb25["nname"] = omb25["use_case_name"].map(norm)
    omb25["sname"] = omb25["use_case_name"].map(squash)
    omb25["ndesc"] = (
        omb25["problem_solved"].fillna("").astype(str) + " " + omb25["benefits"].fillna("").astype(str)
    ).map(norm)

    ids24 = set(doj24["nid"]) - {""}
    ids25 = set(omb25["nid"]) - {""}
    both = ids24 & ids25
    only24 = ids24 - ids25
    only25 = ids25 - ids24

    # 1. Identifier hygiene in DOJ 2024
    section("1. DOJ 2024 identifiers")
    print(f"rows: {len(doj24)}")
    print(f"blank ids: {(doj24['nid'] == '').sum()}")
    dup24 = doj24[doj24["nid"].duplicated(keep=False) & (doj24["nid"] != "")]
    print(f"rows sharing an id: {len(dup24)}")

    # 2. Reconcile DOJ own 2024 vs OMB 2024 v2
    section("2. DOJ own 2024 vs OMB 2024 v2, and the nameless row")
    print(f"DOJ own rows: {len(doj24)}   OMB v2 DOJ rows: {len(omb24)}")
    own_only = doj24[~doj24["nname"].isin(set(omb24["nname"]))]
    print(f"rows in DOJ file only: {len(own_only)}")
    for _, r in own_only.iterrows():
        print(f"  {r['Use Case ID']}, all fields:")
        for col in doj24.columns[:12]:
            val = r[col]
            shown = "(blank)" if pd.isna(val) or str(val).strip() == "" else str(val)[:100]
            print(f"    {col[:60]}: {shown}")

    # 3. Identifier match
    section("3. DOJ 2024 ids matched into OMB 2025")
    print(f"2024 ids: {len(ids24)}   2025 ids: {len(ids25)}   2025 rows: {len(omb25)}")
    print(f"matched: {len(both)}  ({len(both) / len(ids24):.1%} of 2024 ids)")
    print(f"2024 only: {len(only24)}")
    print(f"2025 only: {len(only25)}")

    # 4. Name change, scored
    section("4. Matched ids: name change scored by similarity")
    m = doj24[doj24["nid"].isin(both)][["nid", "Use Case Name", "sname", "ndesc", STAGE_24]].merge(
        omb25[["nid", "use_case_name", "sname", "ndesc", "development_stage"]],
        on="nid",
        suffixes=("_24", "_25"),
    )
    m["name_sim"] = [ratio(a, b) for a, b in zip(m["sname_24"], m["sname_25"])]
    m["desc_sim"] = [ratio(a, b) for a, b in zip(m["ndesc_24"], m["ndesc_25"])]
    exact = (m["sname_24"] == m["sname_25"]).sum()
    cosmetic = ((m["name_sim"] >= COSMETIC) & (m["sname_24"] != m["sname_25"])).sum()
    partial = ((m["name_sim"] >= PARTIAL) & (m["name_sim"] < COSMETIC)).sum()
    substantive = (m["name_sim"] < PARTIAL).sum()
    print(f"matched pairs: {len(m)}")
    print(f"  same after squashing punctuation and spaces: {exact}")
    print(f"  cosmetic change (name similarity >= {COSMETIC}): {cosmetic}")
    print(f"  partial change ({PARTIAL} to {COSMETIC}): {partial}")
    print(f"  substantive change (< {PARTIAL}): {substantive}")
    print()
    print("substantive and partial changes, with description similarity:")
    flagged = m[m["name_sim"] < COSMETIC].sort_values("name_sim")
    for _, r in flagged.head(SHOW).iterrows():
        print(f"  {r['nid']}  name {r['name_sim']:.2f}  desc {r['desc_sim']:.2f}")
        print(f"    2024: {str(r['Use Case Name'])[:90]}")
        print(f"    2025: {str(r['use_case_name'])[:90]}")

    # 5. Duplicate ids in 2025
    section("5. Duplicate ids in OMB 2025 DOJ rows")
    dup25 = omb25[omb25["nid"].duplicated(keep=False) & (omb25["nid"] != "")]
    print(f"rows sharing an id: {len(dup25)}")
    for nid, grp in dup25.groupby("nid"):
        print(f"  {nid}")
        for _, r in grp.iterrows():
            print(f"    {str(r['use_case_name'])[:80]}  |  {r['development_stage']}")

    # 6. Retired in 2024
    section("6. DOJ 2024 retired use cases")
    ret = doj24[doj24["retired"]]
    print(f"retired in 2024: {len(ret)}")
    print(f"  id present in 2025: {ret['nid'].isin(ids25).sum()}")
    print(f"  id absent in 2025: {(~ret['nid'].isin(ids25)).sum()}")
    if ret["nid"].isin(ids25).any():
        carried = omb25[omb25["nid"].isin(set(ret["nid"]))]
        print("  2025 stage of retired ids still present:")
        print(carried["development_stage"].fillna("(blank)").value_counts().to_string())

    # 7. 2024-only ids
    section("7. 2024-only ids: where did they go?")
    gone = doj24[doj24["nid"].isin(only24)].copy()
    new25 = omb25[omb25["nid"].isin(only25)].copy()

    exact_name = dict(zip(new25["sname"], new25["id"]))
    gone["renumbered_to"] = gone["sname"].map(lambda s: exact_name.get(s) if s else None)

    best_id, best_name, best_desc = [], [], []
    for _, r in gone.iterrows():
        top = (None, 0.0, 0.0)
        for _, c in new25.iterrows():
            ns = ratio(r["sname"], c["sname"])
            ds = ratio(r["ndesc"], c["ndesc"])
            if max(ns, ds) > max(top[1], top[2]):
                top = (c["id"], ns, ds)
        best_id.append(top[0])
        best_name.append(top[1])
        best_desc.append(top[2])
    gone["best_2025_id"] = best_id
    gone["best_name_sim"] = best_name
    gone["best_desc_sim"] = best_desc

    def bucket(r):
        if r["nname"] == "":
            return "blank record"
        if pd.notna(r["renumbered_to"]):
            return "renumbered, same name"
        if r["retired"]:
            return "retired in 2024"
        if max(r["best_name_sim"], r["best_desc_sim"]) >= CANDIDATE:
            return "fuzzy candidate"
        return "unexplained"

    gone["bucket"] = gone.apply(bucket, axis=1)
    print(gone["bucket"].value_counts().to_string())
    print()
    print("fuzzy candidates:")
    for _, r in gone[gone["bucket"] == "fuzzy candidate"].head(SHOW).iterrows():
        cand = new25[new25["id"] == r["best_2025_id"]]["use_case_name"]
        cand_name = cand.iloc[0] if len(cand) else ""
        print(f"  {r['nid']} -> {r['best_2025_id']}  name {r['best_name_sim']:.2f}  desc {r['best_desc_sim']:.2f}")
        print(f"    2024: {str(r['Use Case Name'])[:90]}")
        print(f"    2025: {str(cand_name)[:90]}")
    print()
    print("2024 stage of unexplained:")
    unexp = gone[gone["bucket"] == "unexplained"]
    print(unexp[STAGE_24].map(lambda s: norm(s).split(" - ")[0] if norm(s) else "(blank)").value_counts().to_string())

    # 8. 2025-only ids
    section("8. 2025-only ids by 2025 stage")
    print(f"2025-only ids: {len(only25)}   rows: {len(new25)}")
    print(new25["development_stage"].fillna("(blank)").value_counts().to_string())

    # 9. Tally
    section("9. Tentative 2024-side tally")
    tally = {
        "matched by id": len(both),
        **gone["bucket"].value_counts().to_dict(),
    }
    total = 0
    for k, v in tally.items():
        print(f"  {k}: {v}")
        total += v
    print(f"  total: {total}  (2024 ids: {len(ids24)})")

    # Detail files
    m.drop(columns=["sname_24", "sname_25", "ndesc_24", "ndesc_25"]).to_csv(
        OUT / "matched-pairs.csv", index=False
    )
    gone.drop(columns=["sname", "ndesc"]).to_csv(OUT / "2024-only.csv", index=False)
    new25.drop(columns=["sname", "ndesc"]).to_csv(OUT / "2025-only.csv", index=False)
    print()
    print(f"detail files written to {OUT}")


if __name__ == "__main__":
    main()

"""HHS source inspection.

Run from anywhere:
    python hhs-inspect.py

Checks:
  1. HHS 2024 file: real header row, row count, id column.
  2. HHS FY25 file: row count, stage values, withheld flag.
  3. Reconcile HHS FY25 (agency file) with OMB 2025 HHS rows.
  4. Reconcile HHS 2024 (agency file) with OMB 2024 v2 HHS rows.
  5. HHS consolidated commercial file: categories marked Y.

Output goes to the console only.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
HHS = ROOT / "agency-files" / "hhs"
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
SHOW = 10


def norm(text):
    if pd.isna(text):
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def clean_cols(df):
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    return df


def find_col(df, *needles):
    for c in df.columns:
        low = c.lower()
        if all(n in low for n in needles):
            return c
    return None


def read_cp1252(path, header=0):
    df = pd.read_csv(path, encoding="cp1252", encoding_errors="replace", header=header, dtype=str, low_memory=False)
    df = clean_cols(df)
    df = df.dropna(how="all")
    replaced = int(df.apply(lambda col: col.fillna("").str.count("�")).to_numpy().sum())
    return df, replaced


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def stage_short(value):
    s = norm(value)
    s = re.sub(r"^[a-e]\)\s*", "", s)
    return re.split(r"\s+-\s+", s)[0] if s else "(blank)"


def reconcile(label_a, names_a, label_b, names_b):
    a = pd.Series(names_a).map(squash)
    b = pd.Series(names_b).map(squash)
    sa, sb = set(a) - {""}, set(b) - {""}
    print(f"{label_a}: {len(a)} rows, {len(sa)} distinct names")
    print(f"{label_b}: {len(b)} rows, {len(sb)} distinct names")
    only_a = [n for n, s in zip(names_a, a) if s and s not in sb]
    only_b = [n for n, s in zip(names_b, b) if s and s not in sa]
    print(f"names in {label_a} only: {len(only_a)}")
    for n in only_a[:SHOW]:
        print(f"  {str(n)[:90]}")
    print(f"names in {label_b} only: {len(only_b)}")
    for n in only_b[:SHOW]:
        print(f"  {str(n)[:90]}")


def main():
    # 1. HHS 2024
    section("1. HHS 2024 agency file")
    h24, rep = read_cp1252(HHS / "hhs-ai-use-cases-2024-public-inventory.csv", header=1)
    print(f"rows: {len(h24)}   cols: {len(h24.columns)}   replacement characters: {rep}")
    print("columns:")
    for c in h24.columns:
        print(f"  {c[:100]}")
    idc = find_col(h24, "id")
    name24 = find_col(h24, "use case name") or h24.columns[1]
    print()
    print(f"id column: {idc}")
    if idc:
        ids = h24[idc].fillna("").str.strip()
        print(f"  blank ids: {(ids == '').sum()}")
        print(f"  duplicate ids: {ids[ids != ''].duplicated().sum()}")
        print(f"  first: {ids.head(5).tolist()}")
        print(f"  last: {ids.tail(3).tolist()}")
    st24 = find_col(h24, "stage")
    if st24:
        print("2024 stage:")
        print(h24[st24].map(stage_short).value_counts().to_string())

    # 2. HHS FY25
    section("2. HHS FY25 agency file")
    h25, rep = read_cp1252(HHS / "hhs-ai-use-case-inventory-fy25.csv")
    print(f"rows: {len(h25)}   cols: {len(h25.columns)}   replacement characters: {rep}")
    name25 = find_col(h25, "use case name")
    print(f"id-like columns: {[c for c in h25.columns if re.search(r'\\bid\\b', c.lower())]}")
    st25 = find_col(h25, "stage")
    print("2025 stage:")
    print(h25[st25].map(stage_short).value_counts().to_string())
    wh = find_col(h25, "withheld")
    print("withheld:")
    print(h25[wh].fillna("(blank)").map(lambda v: norm(v)[:40] or "(blank)").value_counts().to_string())
    bur = find_col(h25, "bureau")
    print("by bureau, 2025:")
    print(h25[bur].fillna("(blank)").value_counts().head(15).to_string())

    # 3. Reconcile FY25 with OMB 2025
    section("3. HHS FY25 file vs OMB 2025 HHS rows")
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    omb25 = ind[ind["agency"].astype(str).str.strip().str.upper() == "HHS"]
    reconcile("HHS file", h25[name25].tolist(), "OMB 2025", omb25["use_case_name"].tolist())

    # 4. Reconcile 2024 with OMB 2024 v2
    section("4. HHS 2024 file vs OMB 2024 v2 HHS rows")
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    omb24 = v2[v2["3_abr"].astype(str).str.strip().str.upper() == "HHS"]
    omb24v1 = v1[v1["3_abr"].astype(str).str.strip().str.upper() == "HHS"]
    print(f"OMB 2024 original file HHS rows: {len(omb24v1)}")
    reconcile("HHS file", h24[name24].tolist(), "OMB 2024 v2", omb24["2_use_case_name"].tolist())

    # 5. Consolidated commercial
    section("5. HHS consolidated commercial file")
    cons = pd.read_csv(HHS / "hhs-consolidated-ai-use-case-fy25.csv", encoding="utf-8-sig", dtype=str)
    yes = cons[cons["Agency Use (Y/N)?"].fillna("").str.strip().str.upper().str.startswith("Y")]
    print(f"categories: {len(cons)}   marked Y: {len(yes)}")
    for _, r in yes.iterrows():
        print(f"  {str(r['AI Use Case'])[:70]}  |  {str(r['Name of Commercial Product or Service Used'])[:40]}")


if __name__ == "__main__":
    main()

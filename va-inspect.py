"""VA source inspection.

Run from anywhere:
    python va-inspect.py

Checks:
  1. VA 2024 file: header rows, row count, columns, id format.
  2. VA 2025 file: row count, columns, id format, year prefix in ids.
  3. Identifier match, 2024 into 2025.
  4. Reconcile both VA files with OMB's VA rows.
  5. Stage values both years, and the 2024 commercial flag.
  6. VA consolidated commercial file.

Output goes to the console only.
"""

import glob
import re
import unicodedata
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent
VA = ROOT / "agency-files" / "va"
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
    return re.sub(r"\s+", " ", s).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def norm_id(v):
    return "" if pd.isna(v) else re.sub(r"\s+", "", str(v)).upper()


def stage_short(v):
    s = re.sub(r"^[a-e]\)\s*", "", norm(v))
    return re.split(r"\s+-\s+", s)[0] if s else "(blank)"


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def one(pattern):
    hits = glob.glob(str(VA / pattern))
    if not hits:
        raise FileNotFoundError(f"no file matching {pattern} in {VA}")
    return hits[0]


def reconcile(label_a, names_a, label_b, names_b):
    a = [squash(n) for n in names_a]
    b = [squash(n) for n in names_b]
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
    # 1. VA 2024
    section("1. VA 2024 agency file")
    f24 = one("AI-Use-Case-Inventory-VA_BULK*")
    raw = pd.read_excel(f24, sheet_name=0, header=None, dtype=str)
    labels = raw.iloc[3].tolist()
    v24 = raw.iloc[4:].copy()
    v24.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in labels]
    v24 = v24.dropna(how="all")
    idc24 = v24.columns[0]
    v24 = v24[v24[idc24].fillna("").str.strip() != ""]
    print(f"file: {Path(f24).name}")
    print(f"rows: {len(v24)}   cols: {len(v24.columns)}")
    for i, c in enumerate(v24.columns):
        print(f"  {i} {c[:70]} | {str(v24[c].iloc[0])[:50]}")
    ids24 = v24[idc24].map(norm_id)
    print(f"blank ids: {(ids24 == '').sum()}   duplicate ids: {ids24.duplicated().sum()}")
    print(f"first: {ids24.head(3).tolist()}   last: {ids24.tail(2).tolist()}")

    # 2. VA 2025
    section("2. VA 2025 agency file")
    f25 = one("VA-AI-Use-Case-Inventory-2025*")
    v25 = pd.read_excel(f25, sheet_name="All Use Cases", header=1, dtype=str).dropna(how="all")
    v25.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in v25.columns]
    print(f"rows: {len(v25)}   cols: {len(v25.columns)}")
    for i, c in enumerate(v25.columns):
        print(f"  {i} {c[:70]}")
    ids25 = v25["Use Case ID"].map(norm_id)
    print(f"blank ids: {(ids25 == '').sum()}   duplicate ids: {ids25[ids25 != ''].duplicated().sum()}")
    prefix = ids25.str.extract(r"^(VA-\d+)")[0].fillna("(other)")
    print("id year prefix in 2025:")
    print(prefix.value_counts().to_string())

    # 3. Identifier match
    section("3. VA 2024 ids matched into VA 2025")
    s24, s25 = set(ids24) - {""}, set(ids25) - {""}
    both = s24 & s25
    print(f"2024 ids: {len(s24)}   2025 ids: {len(s25)}")
    print(f"matched: {len(both)}  ({len(both) / len(s24):.1%} of 2024 ids)")
    print(f"2024 only: {len(s24 - s25)}   2025 only: {len(s25 - s24)}")
    new_prefix = pd.Series(sorted(s25 - s24)).str.extract(r"^(VA-\d+)")[0].fillna("(other)")
    print("year prefix of 2025-only ids:")
    print(new_prefix.value_counts().to_string())

    # 4. Reconcile with OMB
    section("4. VA files vs OMB VA rows")
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    o24 = v2[v2["3_abr"].astype(str).str.strip().str.upper() == "VA"]
    o24v1 = v1[v1["3_abr"].astype(str).str.strip().str.upper() == "VA"]
    print(f"OMB 2024 original file VA rows: {len(o24v1)}")
    reconcile("VA 2024 file", v24[v24.columns[1]].tolist(), "OMB 2024 v2", o24["2_use_case_name"].tolist())
    print()
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)
    o25 = ind[ind["agency"].astype(str).str.strip().str.upper() == "VA"]
    reconcile("VA 2025 file", v25["Use Case Name"].tolist(), "OMB 2025", o25["use_case_name"].tolist())
    oid = set(o25["id"].map(norm_id)) - {""}
    print(f"OMB 2025 VA ids: {len(oid)}   in VA file: {len(oid & s25)}   OMB only: {len(oid - s25)}   VA file only: {len(s25 - oid)}")

    # 5. Stage and commercial
    section("5. Stage and commercial flag")
    st24 = [c for c in v24.columns if "stage" in c.lower()]
    if st24:
        print("2024 stage:")
        print(v24[st24[0]].map(stage_short).value_counts().to_string())
    print("2025 stage:")
    print(v25["Development Stage"].map(stage_short).value_counts().to_string())
    com = [c for c in v24.columns if "commercial" in c.lower() or "appendix b" in c.lower()]
    if com:
        print("2024 commercial flag:")
        print(v24[com[0]].fillna("(blank)").map(lambda v: str(v)[:70]).value_counts().to_string())
    print("2025 by office:")
    print(v25["VA Admin or Staff Office"].fillna("(blank)").value_counts().head(8).to_string())

    # 6. Consolidated
    section("6. VA consolidated commercial file")
    cons = pd.read_excel(one("VA-AI-Consolidated*"), sheet_name=0, dtype=str)
    cons.columns = [str(c).strip() for c in cons.columns]
    cats = cons[cons.columns[0]].dropna()
    print(f"rows: {len(cons)}   categories listed: {len(cats)}")
    for c in cats:
        print(f"  {str(c)[:90]}")


if __name__ == "__main__":
    main()

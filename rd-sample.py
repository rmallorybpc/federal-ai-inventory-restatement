"""Research and development scope sample for NASA and DOE.

Run from anywhere:
    python rd-sample.py

Steps:
  1. Id crosswalk test: is 2025 NASA-7 the 2023 entry NASA-0007-2023?
     Same test for DOE. Checked against names.
  2. Draw a random sample of 2025 entries with no 2024 or 2023 record,
     20 from NASA and 20 from DOE, seed 20261111.
  3. Write a sheet for classifying each entry against the 2024 and
     2025 scope rules.

Labels:
  research-app   research whose purpose is to develop an AI application
                 for agency use. Excluded in 2024, included in 2025.
  research-basic basic or applied research with no agency application.
                 Excluded in both years.
  operational    AI used in agency operations or decisions. Included in
                 both years.
  unsure

Writes results/scope/rd-sample.csv. Keep results/ out of the public repo.
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
P24 = ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory" / "data"
P25 = ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory" / "Data"
OUT = ROOT / "results" / "scope"
SEED = 20261111
PER_AGENCY = 20


def norm(text):
    if pd.isna(text):
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip().lower()


def squash(text):
    return re.sub(r"[^a-z0-9]", "", norm(text))


def num(v, pattern):
    m = re.search(pattern, str(v or ""))
    return int(m.group(1)) if m else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d23 = pd.read_csv(P24 / "2023_consolidated_ai_inventory_raw.csv", encoding="cp1252",
                      encoding_errors="replace", dtype=str)
    v1 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw.csv", encoding="utf-8", dtype=str)
    v2 = pd.read_csv(P24 / "2024_consolidated_ai_inventory_raw_v2.csv", encoding="cp1252", dtype=str)
    v2.columns = v1.columns
    ind = pd.read_csv(P25 / "2025_individually_reported_AI_use_cases.csv", encoding="utf-8-sig", dtype=str)

    frames = []
    for ag in ["NASA", "DOE"]:
        a23 = d23[d23["Department_Code"].fillna("").str.upper().str.strip() == ag].copy()
        a24 = v2[v2["3_abr"].fillna("").str.upper().str.strip() == ag]
        a25 = ind[ind["agency"].fillna("").str.upper().str.strip() == ag].copy()

        # 1. Id number crosswalk, 2023 to 2025
        a23["n"] = a23["Use_Case_ID"].map(lambda v: num(v, r"-(\d+)-20\d\d$"))
        a25["n"] = a25["id"].map(lambda v: num(v, r"-(\d+)$"))
        by_n = dict(zip(a25["n"], a25["use_case_name"]))
        pairs = [(t, by_n.get(n)) for t, n in zip(a23["Title"], a23["n"]) if n in by_n]
        same = sum(squash(a) == squash(b) for a, b in pairs)
        print(f"{ag}: 2023 numbers found among 2025 ids: {len(pairs)} of {len(a23)}   same name: {same}")
        for a, b in pairs[:4]:
            print(f"    2023: {str(a)[:60]}")
            print(f"    2025: {str(b)[:60]}")

        # 2. Entries with no prior record
        names_prior = set(a23["Title"].map(squash)) | set(a24["2_use_case_name"].map(squash))
        new = a25[~a25["use_case_name"].map(squash).isin(names_prior)]
        print(f"{ag}: 2025 entries with no 2023 or 2024 name match: {len(new)}")
        s = new.sample(n=min(PER_AGENCY, len(new)), random_state=SEED)
        frames.append(s)

    sample = pd.concat(frames)
    stage = sample["development_stage"].map(norm).str.replace(r"^[a-e]\)\s*", "", regex=True).str.split(" ").str[0]
    sheet = pd.DataFrame({
        "agency": sample["agency"],
        "id_2025": sample["id"],
        "name": sample["use_case_name"],
        "bureau": sample["agency_bureau"],
        "stage": stage,
        "topic": sample["topic_area"],
        "classification": sample["classification"],
        "problem": sample["problem_solved"].fillna("").str.slice(0, 500),
        "benefits": sample["benefits"].fillna("").str.slice(0, 400),
        "outputs": sample["system_outputs"].fillna("").str.slice(0, 300),
        "label": "",
        "notes": "",
    })
    sheet.to_csv(OUT / "rd-sample.csv", index=False, encoding="utf-8-sig")
    print()
    print(f"sample written: {OUT / 'rd-sample.csv'}  ({len(sheet)} rows)")
    print("stage in the sample:")
    print(pd.crosstab(sheet["agency"], sheet["stage"]).to_string())


if __name__ == "__main__":
    main()

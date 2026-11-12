"""Diagnose HHS 2025 retired rows that found no 2024 partner.

Run from anywhere:
    python hhs-anchor.py

For each 2025 row HHS marked retired whose best 2024 match scored
below 0.5 within its division:
  1. Search all of HHS 2024, ignoring division.
  2. Search the HHS FY23 file, if agency-files/hhs holds it.
This separates three causes: a division mismatch, a use case last
reported in 2023, or a name change too large for text matching.

Reuses the loading and scoring from hhs-match.py.
"""

import re
from pathlib import Path

import pandas as pd

import importlib.util

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("hm", ROOT / "hhs-match.py")
hm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hm)

FY23 = ROOT / "agency-files" / "hhs" / "hhs-ai-use-cases-2023-public-inventory.csv"
LOW = 0.5


def load23():
    if not FY23.exists():
        return None
    for header in range(0, 5):
        d = pd.read_csv(FY23, encoding="cp1252", encoding_errors="replace", header=header, dtype=str)
        name_cols = [c for c in d.columns if re.search(r"use\s*case\s*name|^name$|title", str(c), re.I)]
        if name_cols:
            d = d.dropna(how="all")
            out = pd.DataFrame({"name": d[name_cols[0]].values})
            text = d.fillna("").astype(str).agg(" ".join, axis=1).values
            out["sname"] = out["name"].map(hm.squash)
            out["words"] = [hm.words(t) for t in text]
            out["src"] = "FY23"
            return out
    print("FY23 file found but no name column detected. Columns:")
    print(list(pd.read_csv(FY23, encoding="cp1252", encoding_errors="replace", dtype=str, nrows=1).columns))
    return None


def main():
    h24, h25 = hm.load()
    ret = h25[h25["stage_s"] == "retired"]
    h23 = load23()
    print(f"FY23 file: {'loaded, ' + str(len(h23)) + ' rows' if h23 is not None else 'not present'}")

    rows = []
    for j, c in ret.iterrows():
        pool = h24[h24["opdiv"] == c["opdiv"]]
        pool = pool if len(pool) else h24
        within = hm.ranked(c, pool)[0][1]
        if within >= LOW:
            continue
        allhhs = hm.ranked(c, h24)[0]
        rec = {
            "key": c["key"],
            "name": c["name"],
            "opdiv": c["opdiv"],
            "within_div": round(within, 2),
            "all_hhs": round(allhhs[1], 2),
            "all_hhs_name": h24.loc[allhhs[0], "name"],
            "all_hhs_opdiv": h24.loc[allhhs[0], "opdiv"],
        }
        if h23 is not None:
            t = hm.ranked(c, h23)[0]
            rec["fy23"] = round(t[1], 2)
            rec["fy23_name"] = h23.loc[t[0], "name"]
        rows.append(rec)

    d = pd.DataFrame(rows)
    print(f"retired 2025 rows with no partner in their division: {len(d)}")
    print()
    for _, r in d.iterrows():
        print(f"{r['key']}  [{r['opdiv']}]  {str(r['name'])[:70]}")
        print(f"    all HHS 2024  {r['all_hhs']:.2f}  [{r['all_hhs_opdiv']}]  {str(r['all_hhs_name'])[:60]}")
        if "fy23" in r:
            print(f"    FY23          {r['fy23']:.2f}  {str(r['fy23_name'])[:60]}")
    print()
    print(f"found across divisions (>= {LOW}): {(d['all_hhs'] >= LOW).sum()}")
    if "fy23" in d:
        print(f"found in FY23 (>= {LOW}): {(d['fy23'] >= LOW).sum()}")
    d.to_csv(hm.OUT / "retired-anchor-misses.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

"""VA identifier crosswalk, matcher calibration, and review sheet.

Run from anywhere:
    python va-match.py

VA changed its id format between years: VA-36 in 2024, VA-24-1069 in
2025. This script tests whether VA-24-NNNN in 2025 is VA-NNNN from 2024.

Steps:
  1. Build the id crosswalk on the number and check it against names.
  2. Calibrate the text matcher against the crosswalk. The matcher runs
     without ids, within each VA office, and is scored on the ids.
  3. 2024-side outcomes by id, including 2025 stage.
  4. Commercial test: 2024 rows flagged as listed commercial products.
  5. Growth with retired entries excluded.
  6. Write the review sheet for 2024 rows with no id partner, with no
     proposed labels, and the full 2025 list.

Outputs go to results/va-pilot/. Keep results/ out of the public repo.
"""

import difflib
import glob
import re
import unicodedata
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parent
VA = ROOT / "agency-files" / "va"
OUT = ROOT / "results" / "va-pilot"
TOP_N = 3
STOP = {
    "the", "and", "for", "with", "that", "this", "from", "are", "use", "used",
    "ai", "data", "will", "can", "into", "its", "their", "which", "has", "have",
    "va", "case", "system", "tool", "tools", "using", "information", "model",
    "models", "not", "our", "also", "these", "such", "based", "veterans",
}


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


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", norm(text)) if len(w) > 2 and w not in STOP}


def name_sim(a, b):
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def stage_short(v):
    s = re.sub(r"^[a-e]\)\s*", "", norm(v))
    return re.split(r"\s+-\s+", s)[0] if s else "(blank)"


def office(v):
    return str(v or "").split(":")[0].strip().upper()


def one(pattern):
    return glob.glob(str(VA / pattern))[0]


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def load():
    raw = pd.read_excel(one("AI-Use-Case-Inventory-VA_BULK*"), sheet_name=0, header=None, dtype=str)
    d = raw.iloc[4:].dropna(how="all")
    v24 = pd.DataFrame({
        "id": d[0].str.strip(),
        "name": d[1],
        "bureau": d[3],
        "commercial": d[6],
        "purpose": d[7],
        "outputs": d[8],
        "stage": d[9],
    })
    v24 = v24[v24["id"].fillna("") != ""].reset_index(drop=True)
    v24["num"] = v24["id"].str.extract(r"(\d+)\s*$")[0].astype(float)

    r25 = pd.read_excel(one("VA-AI-Use-Case-Inventory-2025*"), sheet_name="All Use Cases", header=1, dtype=str).dropna(how="all")
    r25.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in r25.columns]
    v25 = pd.DataFrame({
        "id": r25["Use Case ID"].str.strip().values,
        "name": r25["Use Case Name"].values,
        "bureau": r25["VA Admin or Staff Office"].values,
        "stage": r25["Development Stage"].values,
        "problem": r25["Problem to be Solved"].values,
        "benefits": r25["Expected Benefits"].values,
        "outputs": r25["AI System Outputs"].values,
    })
    parts = v25["id"].str.extract(r"^VA-(\d+)-(\d+)$")
    v25["year"] = parts[0]
    v25["num"] = parts[1].astype(float)

    for d_ in (v24, v25):
        d_["office"] = d_["bureau"].map(office)
        d_["sname"] = d_["name"].map(squash)
        d_["stage_s"] = d_["stage"].map(stage_short)
    v24["words"] = (v24["name"].fillna("") + " " + v24["purpose"].fillna("") + " " + v24["outputs"].fillna("")).map(words)
    v25["words"] = (v25["name"].fillna("") + " " + v25["problem"].fillna("") + " "
                    + v25["benefits"].fillna("") + " " + v25["outputs"].fillna("")).map(words)
    return v24, v25


def ranked(row, pool):
    out = []
    for j, c in pool.iterrows():
        ns = name_sim(row["sname"], c["sname"])
        dj = jaccard(row["words"], c["words"])
        out.append((j, max(ns, dj)))
    out.sort(key=lambda t: -t[1])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    v24, v25 = load()

    # 1. Crosswalk
    section("1. Id crosswalk: is VA-24-NNNN the 2024 id VA-NNNN?")
    c24 = v25[v25["year"] == "24"]
    num_to_j = dict(zip(c24["num"], c24.index))
    v24["j"] = v24["num"].map(num_to_j)
    hit = v24[v24["j"].notna()].copy()
    hit["j"] = hit["j"].astype(int)
    sims = [name_sim(a, v25.loc[j, "sname"]) for a, j in zip(hit["sname"], hit["j"])]
    hit["nsim"] = sims
    print(f"2024 ids: {len(v24)}   2025 ids with 24 prefix: {len(c24)}   with 25 prefix: {(v25['year'] == '25').sum()}")
    print(f"2024 numbers found among 24-prefix ids: {len(hit)}  ({len(hit) / len(v24):.1%})")
    print(f"  same name: {(hit['nsim'] == 1).sum()}")
    print(f"  similar name (0.6 or more): {((hit['nsim'] >= 0.6) & (hit['nsim'] < 1)).sum()}")
    print(f"  different name (under 0.6): {(hit['nsim'] < 0.6).sum()}")
    for _, r in hit[hit["nsim"] < 0.6].head(10).iterrows():
        print(f"    {r['id']} -> {v25.loc[r['j'], 'id']}  {r['nsim']:.2f}")
        print(f"      2024: {str(r['name'])[:80]}")
        print(f"      2025: {str(v25.loc[r['j'], 'name'])[:80]}")
    orphan25 = c24[~c24["num"].isin(set(v24["num"]))]
    print(f"24-prefix ids in 2025 with no 2024 row: {len(orphan25)}")
    for _, r in orphan25.head(10).iterrows():
        print(f"    {r['id']}  {r['stage_s']}  {str(r['name'])[:70]}")

    truth = dict(zip(hit.index, hit["j"]))

    # 2. Calibration
    section("2. Text matcher scored against the id crosswalk")
    best24, best25 = {}, {}
    for i, r in v24.iterrows():
        pool = v25[v25["office"] == r["office"]]
        best24[i] = ranked(r, pool if len(pool) else v25)
    for j, c in v25.iterrows():
        pool = v24[v24["office"] == c["office"]]
        best25[j] = ranked(c, pool if len(pool) else v24)
    rows = []
    for i, r in v24.iterrows():
        j, score = best24[i][0]
        mutual = best25[j][0][0] == i
        if r["sname"] and r["sname"] == v25.loc[j, "sname"]:
            tier = "exact name"
        elif mutual and score >= 0.6:
            tier = "mutual best >= 0.6"
        else:
            tier = "needs review"
        t = truth.get(i)
        rows.append({"i": i, "tier": tier, "j": j, "score": score,
                     "has_partner": t is not None, "correct": t == j,
                     "in_top3": t in [x[0] for x in best24[i][:TOP_N]] if t is not None else False})
    cal = pd.DataFrame(rows)
    print(f"{'tier':22} {'rows':>5} {'right':>6} {'wrong pair':>11} {'no true partner':>16}")
    for tier in ["exact name", "mutual best >= 0.6", "needs review"]:
        g = cal[cal["tier"] == tier]
        right = g["correct"].sum()
        wrong = (g["has_partner"] & ~g["correct"]).sum()
        none = (~g["has_partner"]).sum()
        print(f"{tier:22} {len(g):5} {right:6} {wrong:11} {none:16}")
    auto = cal[cal["tier"] != "needs review"]
    if len(auto):
        err = (~auto["correct"]).sum()
        print(f"automatic matches: {len(auto)}   wrong: {err}  ({err / len(auto):.1%})")
    partners = cal[cal["has_partner"]]
    print(f"true pairs: {len(partners)}   caught automatically: {(partners['tier'] != 'needs review').sum()}"
          f"   true partner in top {TOP_N}: {partners['in_top3'].sum()}")

    # 3. 2024-side outcomes
    section("3. VA 2024 use cases by id outcome")
    v24["stage25"] = v24["j"].map(lambda j: v25.loc[int(j), "stage_s"] if pd.notna(j) else "no 2025 id")
    print(v24["stage25"].value_counts().to_string())
    print()
    print("2024 stage of rows with no 2025 id:")
    print(v24[v24["j"].isna()]["stage_s"].value_counts().to_string())
    print()
    print("2025 entries by id prefix and stage:")
    print(pd.crosstab(v25["year"].fillna("other"), v25["stage_s"]).to_string())

    # 4. Commercial
    section("4. 2024 rows flagged as listed commercial products")
    flag = v24["commercial"].fillna("").map(norm)
    listed = v24[(flag != "") & (~flag.str.startswith("none of the above"))]
    print(f"flagged: {len(listed)} of {len(v24)}")
    print(pd.crosstab(listed["commercial"].map(lambda v: str(v)[:45]), listed["stage25"]).to_string())

    # 5. Active growth
    section("5. VA growth with retired entries excluded")
    a24 = (v24["stage_s"] != "retired").sum()
    a25 = (v25["stage_s"] != "retired").sum()
    print(f"  VA files, all entries:      {len(v24)} -> {len(v25)}   growth {len(v25) / len(v24) - 1:.1%}")
    print(f"  active only:                {a24} -> {a25}   growth {a25 / a24 - 1:.1%}")
    print(f"  retired in 2025: {len(v25) - a25}   of which carry a 2024 id: {((v25['stage_s'] == 'retired') & (v25['year'] == '24')).sum()}")

    # 6. Files
    v25[["id", "name", "bureau", "stage", "problem", "benefits"]].to_csv(OUT / "va-2025-all.csv", index=False, encoding="utf-8-sig")
    sheet = []
    for i, r in v24[v24["j"].isna()].iterrows():
        rec = {
            "id_2024": r["id"], "name_2024": r["name"], "office": r["office"],
            "stage_2024": r["stage_s"], "commercial_2024": r["commercial"],
            "purpose_2024": str(r["purpose"])[:300],
        }
        for k, (j, score) in enumerate(best24[i][:TOP_N], start=1):
            c = v25.loc[j]
            rec[f"c{k}_id"] = c["id"]
            rec[f"c{k}_name"] = c["name"]
            rec[f"c{k}_stage"] = c["stage_s"]
            rec[f"c{k}_score"] = round(score, 2)
            rec[f"c{k}_problem"] = str(c["problem"])[:300]
        rec["label"] = ""
        rec["matched_2025_id"] = ""
        rec["notes"] = ""
        sheet.append(rec)
    review = pd.DataFrame(sheet)
    review.to_csv(OUT / "review-va-2024.csv", index=False, encoding="utf-8-sig")
    cal.to_csv(OUT / "calibration-va.csv", index=False)
    print()
    print(f"full 2025 list: {OUT / 'va-2025-all.csv'}")
    print(f"review sheet:   {OUT / 'review-va-2024.csv'}  ({len(review)} rows, no proposals)")


if __name__ == "__main__":
    main()

"""HHS text matching pilot. 2024 has ids, 2025 has none.

Run from anywhere:
    python hhs-match.py

Steps:
  1. Load HHS 2024 (271 rows with ids) and HHS FY25 (446 rows, no ids).
     Each 2025 row gets a stable key, H25-0001 and up, in file order.
  2. Compare entries within the same operating division (NIH to NIH,
     CDC to CDC). Score = max(name similarity, word overlap), the same
     scoring calibrated on DOJ. System name agreement is reported as a
     separate signal.
  3. Retired anchor: 2025 rows marked retired were, by HHS's own
     definition, reported in 2024. Check how well each finds a partner.
  4. Preliminary sort of all 2024 rows: exact name, mutual best match,
     or needs review.
  5. Commercial test: 2024 rows flagged as listed commercial products.
     Did they stay in the 2025 individual list?
  6. Write the review sheet and the full 2025 list to results/hhs-pilot/.

Keep results/ out of the public repo.
"""

import difflib
import re
import unicodedata
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
HHS = ROOT / "agency-files" / "hhs"
OUT = ROOT / "results" / "hhs-pilot"
TOP_N = 3
THRESHOLDS = [0.5, 0.6, 0.7, 0.8, 0.9]
STOP = {
    "the", "and", "for", "with", "that", "this", "from", "are", "use", "used",
    "ai", "data", "will", "can", "into", "its", "their", "which", "has", "have",
    "hhs", "case", "system", "tool", "tools", "using", "information", "model",
    "models", "not", "our", "also", "these", "such", "based",
}


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


def opdiv(value):
    s = str(value or "").strip().upper()
    s = re.sub(r"^HHS\s*/\s*", "", s)
    return re.split(r"[/\s-]", s)[0] if s else ""


def stage_short(value):
    s = norm(value)
    s = re.sub(r"^[a-e]\)\s*", "", s)
    return re.split(r"\s+-\s+", s)[0] if s else "(blank)"


def find_col(df, *needles):
    for c in df.columns:
        low = re.sub(r"\s+", " ", str(c)).lower()
        if all(n in low for n in needles):
            return c
    raise KeyError(f"no column with {needles}")


def generic_system(s):
    return s in {"", "na", "nan", "none", "tbd", "notapplicable", "nottapplicable"}


def load():
    raw = pd.read_csv(HHS / "hhs-ai-use-cases-2024-public-inventory.csv",
                      encoding="cp1252", header=2, dtype=str)
    raw = raw[raw.iloc[:, 0].fillna("").str.match(r"^HHS-")].copy()
    cols = list(raw.columns)
    h24 = pd.DataFrame({
        "id": raw[cols[0]].str.strip(),
        "name": raw[cols[1]],
        "bureau": raw[cols[3]],
        "commercial": raw[cols[5]],
        "purpose": raw[cols[6]],
        "outputs": raw[cols[7]],
        "stage": raw[cols[8]],
        "system": raw[cols[30]],
    }).reset_index(drop=True)

    r25 = pd.read_csv(HHS / "hhs-ai-use-case-inventory-fy25.csv",
                      encoding="cp1252", dtype=str).dropna(how="all")
    h25 = pd.DataFrame({
        "key": [f"H25-{i:04d}" for i in range(1, len(r25) + 1)],
        "name": r25[find_col(r25, "use case name")].values,
        "bureau": r25[find_col(r25, "bureau")].values,
        "stage": r25[find_col(r25, "stage of development")].values,
        "problem": r25[find_col(r25, "problem")].values,
        "benefits": r25[find_col(r25, "expected benefits")].values,
        "outputs": r25[find_col(r25, "outputs")].values,
        "system": r25[find_col(r25, "system(s) name")].values,
        "vendor": r25[find_col(r25, "vendor")].values,
    })

    for d in (h24, h25):
        d["opdiv"] = d["bureau"].map(opdiv)
        d["sname"] = d["name"].map(squash)
        d["ssys"] = d["system"].map(squash)
        d["stage_s"] = d["stage"].map(stage_short)
    h24["words"] = (h24["name"].fillna("") + " " + h24["purpose"].fillna("") + " " + h24["outputs"].fillna("")).map(words)
    h25["words"] = (h25["name"].fillna("") + " " + h25["problem"].fillna("") + " "
                    + h25["benefits"].fillna("") + " " + h25["outputs"].fillna("")).map(words)
    return h24, h25


def ranked(row, pool):
    out = []
    for j, c in pool.iterrows():
        ns = name_sim(row["sname"], c["sname"])
        dj = jaccard(row["words"], c["words"])
        sysm = (not generic_system(row["ssys"])) and row["ssys"] == c["ssys"]
        out.append((j, max(ns, dj), ns, dj, sysm))
    out.sort(key=lambda t: -t[1])
    return out


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    h24, h25 = load()

    section("1. Loaded")
    print(f"2024 rows with ids: {len(h24)}")
    print(f"2025 rows: {len(h25)}")
    print("operating divisions, 2024 vs 2025:")
    od = pd.DataFrame({"2024": h24["opdiv"].value_counts(), "2025": h25["opdiv"].value_counts()}).fillna(0).astype(int)
    print(od.sort_values("2025", ascending=False).to_string())
    missing = sorted(set(h24["opdiv"]) - set(h25["opdiv"]))
    print(f"2024 divisions with no 2025 rows: {missing}")
    print()
    print("2024 stage:")
    print(h24["stage_s"].value_counts().to_string())

    def pool_for(div, frame):
        p = frame[frame["opdiv"] == div]
        return p if len(p) else frame

    # Rank both directions
    best24 = {}
    for i, r in h24.iterrows():
        best24[i] = ranked(r, pool_for(r["opdiv"], h25))
    best25 = {}
    for j, c in h25.iterrows():
        rr = c.copy()
        best25[j] = ranked(rr, pool_for(c["opdiv"], h24))

    # 3. Retired anchor
    section("3. Retired anchor: 2025 rows HHS marked retired")
    ret = h25[h25["stage_s"] == "retired"]
    scores = []
    exact = 0
    for j, c in ret.iterrows():
        top = best25[j][0]
        scores.append(top[1])
        if h24.loc[top[0], "sname"] == c["sname"]:
            exact += 1
    s = pd.Series(scores)
    print(f"retired rows: {len(ret)}")
    print(f"best 2024 partner has the exact same name: {exact}")
    for t in THRESHOLDS:
        print(f"  best score >= {t:.1f}: {(s >= t).sum()}")
    print(f"  lowest best score: {s.min():.2f}")
    print("Every retired row should have a 2024 partner. Rows with a low best")
    print("score show how often HHS text drifts beyond what matching can catch.")

    # 4. Preliminary sort of 2024 rows
    section("4. 2024 rows: preliminary sort")
    rows = []
    for i, r in h24.iterrows():
        top = best24[i][0]
        j = top[0]
        mutual = best25[j][0][0] == i
        exact_name = r["sname"] != "" and r["sname"] == h25.loc[j, "sname"]
        if exact_name:
            cls = "exact name"
        elif mutual and top[1] >= 0.6:
            cls = "mutual best >= 0.6"
        else:
            cls = "needs review"
        rows.append({"i": i, "class": cls, "score": top[1], "j": j, "sys": top[4]})
    pre = pd.DataFrame(rows)
    print(pre["class"].value_counts().to_string())
    print(f"top candidate shares a system name: {pre['sys'].sum()}")
    used = pre[pre["class"] != "needs review"]["j"]
    print(f"2025 rows claimed by more than one 2024 row: {used.duplicated().sum()}")
    print()
    print("2024 stage of rows needing review:")
    print(h24.loc[pre[pre["class"] == "needs review"]["i"], "stage_s"].value_counts().to_string())

    # 2025 rows with no likely 2024 partner
    claimed = set(pre[pre["class"] != "needs review"]["j"])
    new25 = h25[~h25.index.isin(claimed)]
    print()
    print(f"2025 rows not claimed by an exact or mutual match: {len(new25)}")
    print(new25["stage_s"].value_counts().to_string())

    # 5. Commercial test
    section("5. 2024 rows flagged as listed commercial products")
    flag = h24["commercial"].fillna("").map(norm)
    listed = h24[(flag != "") & (~flag.str.startswith("none of the above"))]
    print(f"flagged rows: {len(listed)}  (blank: {(flag == '').sum()})")
    if len(listed):
        lp = pre.set_index("i").loc[listed.index]
        print(lp["class"].value_counts().to_string())
        print("category, preliminary class:")
        for i in listed.index:
            print(f"  {str(h24.loc[i, 'commercial'])[:55]:55} | {pre.loc[pre['i'] == i, 'class'].iloc[0]}")

    # 6. Write files
    full = h25[["key", "name", "bureau", "stage", "system", "vendor", "problem", "benefits"]]
    full.to_csv(OUT / "hhs-2025-all.csv", index=False, encoding="utf-8-sig")

    sheet = []
    for i, r in h24.iterrows():
        p = pre[pre["i"] == i].iloc[0]
        rec = {
            "id_2024": r["id"],
            "name_2024": r["name"],
            "opdiv": r["opdiv"],
            "stage_2024": r["stage_s"],
            "commercial_2024": r["commercial"],
            "system_2024": r["system"],
            "purpose_2024": str(r["purpose"])[:300],
            "preliminary": p["class"],
        }
        for k, (j, best, ns, dj, sysm) in enumerate(best24[i][:TOP_N], start=1):
            c = h25.loc[j]
            rec[f"c{k}_key"] = c["key"]
            rec[f"c{k}_name"] = c["name"]
            rec[f"c{k}_stage"] = c["stage_s"]
            rec[f"c{k}_score"] = round(best, 2)
            rec[f"c{k}_system_match"] = sysm
            rec[f"c{k}_problem"] = str(c["problem"])[:300]
        rec["label"] = ""
        rec["matched_2025_key"] = ""
        rec["notes"] = ""
        sheet.append(rec)
    review = pd.DataFrame(sheet)
    review.to_csv(OUT / "review-hhs-2024.csv", index=False, encoding="utf-8-sig")

    print()
    print(f"full 2025 list: {OUT / 'hhs-2025-all.csv'}")
    print(f"review sheet:   {OUT / 'review-hhs-2024.csv'}  ({len(review)} rows)")


if __name__ == "__main__":
    main()

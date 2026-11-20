"""Build the VA blind test files.

Run from anywhere:
    python va-blind.py

VA's 2025 ids contain the 2024 id number, so they would give the answer
away. This script hides them. Each 2025 entry gets a masked key, V25-001
and up, in shuffled order.

Writes to results/va-pilot/:
  va-2025-masked.csv             full 2025 list, masked keys, for searching
  review-va-blind-analyst.csv    the review rows, for the analyst to label
  review-va-blind-ai.csv         the same rows, for the AI-assisted rater
  va-blind-truth.csv             the answers. Do not open before labeling.

Labels: match (with the masked key in matched_key), gone, or unsure.
"""

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("vm", ROOT / "va-match.py")
vm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vm)

SEED = 20261111
TOP_N = 3


def main():
    out = vm.OUT
    out.mkdir(parents=True, exist_ok=True)
    v24, v25 = vm.load()

    # Truth from the id number
    c24 = v25[v25["year"] == "24"]
    num_to_j = dict(zip(c24["num"], c24.index))
    v24["j"] = v24["num"].map(num_to_j)

    # Masked keys in shuffled order
    order = v25.sample(frac=1, random_state=SEED).index
    key = {j: f"V25-{n:03d}" for n, j in enumerate(order, start=1)}
    v25["key"] = v25.index.map(key)

    # Tiers, same rules as va-match.py
    best24, best25 = {}, {}
    for i, r in v24.iterrows():
        pool = v25[v25["office"] == r["office"]]
        best24[i] = vm.ranked(r, pool if len(pool) else v25)
    for j, c in v25.iterrows():
        pool = v24[v24["office"] == c["office"]]
        best25[j] = vm.ranked(c, pool if len(pool) else v24)
    review = []
    for i, r in v24.iterrows():
        j, score = best24[i][0]
        mutual = best25[j][0][0] == i
        exact = r["sname"] and r["sname"] == v25.loc[j, "sname"]
        if not exact and not (mutual and score >= 0.6):
            review.append(i)

    rows, truth = [], []
    for i in pd.Series(review).sample(frac=1, random_state=SEED):
        r = v24.loc[i]
        rec = {
            "id_2024": r["id"], "name_2024": r["name"], "office": r["office"],
            "stage_2024": r["stage_s"], "purpose_2024": str(r["purpose"])[:400],
        }
        for k, (j, score) in enumerate(best24[i][:TOP_N], start=1):
            c = v25.loc[j]
            rec[f"c{k}_key"] = c["key"]
            rec[f"c{k}_name"] = c["name"]
            rec[f"c{k}_stage"] = c["stage_s"]
            rec[f"c{k}_score"] = round(score, 2)
            rec[f"c{k}_problem"] = str(c["problem"])[:300]
        rec["label"] = ""
        rec["matched_key"] = ""
        rec["notes"] = ""
        rows.append(rec)
        truth.append({"id_2024": r["id"],
                      "true_key": key[int(r["j"])] if pd.notna(r["j"]) else "",
                      "true_id_2025": v25.loc[int(r["j"]), "id"] if pd.notna(r["j"]) else ""})

    sheet = pd.DataFrame(rows)
    sheet.to_csv(out / "review-va-blind-analyst.csv", index=False, encoding="utf-8-sig")
    sheet.to_csv(out / "review-va-blind-ai.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(truth).to_csv(out / "va-blind-truth.csv", index=False, encoding="utf-8-sig")
    masked = v25.sort_values("key")[["key", "name", "bureau", "stage", "problem", "benefits"]]
    masked.to_csv(out / "va-2025-masked.csv", index=False, encoding="utf-8-sig")

    print(f"review rows: {len(sheet)}")
    print(f"masked 2025 list: {len(masked)} entries")
    print(f"files written to {out}")
    print()
    print("Do not open va-blind-truth.csv, va-2025-all.csv, or review-va-2024.csv")
    print("until your labels are saved. They contain the answers.")


if __name__ == "__main__":
    main()

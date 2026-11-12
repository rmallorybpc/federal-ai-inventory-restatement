"""Draw the HHS review sample.

Run from anywhere:
    python hhs-sample.py

Reads results/hhs-pilot/review-hhs-2024.csv, written by hhs-match.py.
From the rows marked "needs review":
  Part 1: every row HHS flagged in 2024 as a listed commercial product.
  Part 2: a random sample of the remaining rows, fixed seed.

The seed is fixed so the same sample comes out every time. Record it in
the definition spec. Writes results/hhs-pilot/review-hhs-sample.csv.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "hhs-pilot"
SEED = 20261111
SAMPLE = 40


def main():
    d = pd.read_csv(OUT / "review-hhs-2024.csv", encoding="utf-8-sig", dtype=str).fillna("")
    review = d[d["preliminary"] == "needs review"].copy()
    flag = review["commercial_2024"].str.strip().str.lower()
    commercial = (flag != "") & (~flag.str.startswith("none of the above"))

    part1 = review[commercial].copy()
    part1.insert(0, "part", "1 commercial")
    rest = review[~commercial]
    n = min(SAMPLE, len(rest))
    part2 = rest.sample(n=n, random_state=SEED).copy()
    part2.insert(0, "part", "2 random")

    sample = pd.concat([part1, part2]).sort_values(["part", "id_2024"])
    sample.to_csv(OUT / "review-hhs-sample.csv", index=False, encoding="utf-8-sig")

    print(f"needs review: {len(review)}")
    print(f"part 1, commercial: {len(part1)}")
    print(f"part 2, random {n} of {len(rest)} (seed {SEED})")
    print(f"sample written: {OUT / 'review-hhs-sample.csv'}  ({len(sample)} rows)")
    print()
    print("2024 stage in the sample:")
    print(sample["stage_2024"].value_counts().to_string())
    print()
    print("division in the sample:")
    print(sample["opdiv"].value_counts().to_string())


if __name__ == "__main__":
    main()

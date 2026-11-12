"""HHS pilot tally: final labels, sample estimates, restatement.

Run from anywhere:
    python hhs-tally.py

Reads:
  results/hhs-pilot/review-hhs-2024.csv    all 271 rows, preliminary class
  results/hhs-pilot/review-hhs-sample.csv  the 55 labeled rows

For each sample row the final label is your entry in the label column
when filled, otherwise the proposed label.

Part 1 (commercial) is a full count. Part 2 (random) is a sample, so its
label counts are scaled up to the whole pool of rows it was drawn from,
with a 95 percent range. Exact and mutual matches are counted as
continuing without review.

Output goes to the console only.
"""

import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results" / "hhs-pilot"
VALID = {"continues", "renamed", "merged", "retired", "gone", "scope", "cots", "unsure"}
PUBLISHED_2024 = 271
PUBLISHED_2025 = 446


def clean(v):
    return "" if pd.isna(v) else str(v).strip()


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def estimate(k, n, pool):
    """Scale k of n sampled rows to a pool, with a 95 percent range.
    Normal approximation with finite population correction."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    fpc = math.sqrt((pool - n) / (pool - 1)) if pool > 1 else 0
    se = math.sqrt(p * (1 - p) / n) * fpc
    lo = max(0.0, p - 1.96 * se) * pool
    hi = min(1.0, p + 1.96 * se) * pool
    return p * pool, lo, hi


def growth(new, old):
    return f"{new / old - 1:.1%}"


def main():
    full = pd.read_csv(OUT / "review-hhs-2024.csv", encoding="utf-8-sig", dtype=str).fillna("")
    s = pd.read_csv(OUT / "review-hhs-sample.csv", encoding="utf-8-sig", dtype=str).fillna("")

    s["mine"] = s["label"].map(clean).str.lower()
    s["prop"] = s["proposed_label"].map(clean).str.lower()
    s["final"] = s.apply(lambda r: r["mine"] or r["prop"], axis=1)

    section("1. Label source and agreement")
    filled = s[s["mine"] != ""]
    print(f"sample rows: {len(s)}   labeled by you: {len(filled)}   using proposed label: {len(s) - len(filled)}")
    bad = s[~s["final"].isin(VALID)]
    if len(bad):
        print(f"invalid labels, fix before trusting the tally: {len(bad)}")
        print(bad[["id_2024", "final"]].to_string(index=False))
    if len(filled):
        agree = (filled["mine"] == filled["prop"]).sum()
        print(f"agreement with proposal: {agree} of {len(filled)} ({agree / len(filled):.0%})")
        for _, r in filled[filled["mine"] != filled["prop"]].iterrows():
            print(f"  {r['id_2024']}  proposed {r['prop']}  yours {r['mine']}  |  {clean(r['name_2024'])[:50]}")

    # Populations
    auto = full[full["preliminary"] != "needs review"]
    review = full[full["preliminary"] == "needs review"]
    p1 = s[s["part"].str.startswith("1")]
    p2 = s[s["part"].str.startswith("2")]
    pool2 = len(review) - len(p1)

    section("2. Counts by part")
    print(f"exact or mutual match, counted as continuing: {len(auto)}")
    print(f"part 1, commercial, full count: {len(p1)}")
    print(p1["final"].value_counts().to_string())
    print(f"part 2, random {len(p2)} of {pool2}:")
    print(p2["final"].value_counts().to_string())

    section("3. HHS 2024-side decomposition, estimated")
    print(f"{'outcome':26} {'estimate':>9}   {'95% range':>13}")
    rows = {}
    labels = ["continues", "renamed", "merged", "retired", "cots", "scope", "gone", "unsure"]
    for lab in labels:
        k1 = (p1["final"] == lab).sum()
        k2 = (p2["final"] == lab).sum()
        est, lo, hi = estimate(k2, len(p2), pool2)
        base = k1 + (len(auto) if lab == "continues" else 0)
        rows[lab] = (base + est, base + lo, base + hi)
        if base + est > 0:
            print(f"  {lab:24} {base + est:9.0f}   {base + lo:5.0f} to {base + hi:4.0f}")
    total = sum(v[0] for v in rows.values())
    print(f"  {'total':24} {total:9.0f}   (2024 use cases: {len(full)})")
    cont = rows["continues"][0] + rows["renamed"][0] + rows["merged"][0]
    print()
    print(f"continue in some form: about {cont:.0f} of {len(full)} ({cont / len(full):.0%})")
    g = rows["gone"]
    print(f"gone, no counterpart and not retired: about {g[0]:.0f} ({g[1]:.0f} to {g[2]:.0f}), "
          f"{g[0] / len(full):.0%} of 2024")

    section("4. HHS restatement under each ruler, preliminary")
    adj = rows["merged"][0] + rows["cots"][0] + rows["scope"][0]
    adj_lo = rows["merged"][1] + rows["cots"][1] + rows["scope"][1]
    adj_hi = rows["merged"][2] + rows["cots"][2] + rows["scope"][2]
    old, pub = PUBLISHED_2024, PUBLISHED_2025
    print(f"  published, HHS files:     {old} -> {pub}   growth {growth(pub, old)}")
    print(f"  2024 ruler, 2025 restated: {old} -> {pub + adj:.0f}   growth {growth(pub + adj, old)}"
          f"   range {growth(pub + adj_lo, old)} to {growth(pub + adj_hi, old)}")
    print(f"  2025 ruler, 2024 restated: {old - adj:.0f} -> {pub}   growth {growth(pub, old - adj)}"
          f"   range {growth(pub, old - adj_lo)} to {growth(pub, old - adj_hi)}")
    print()
    print("Adjustments: merged, cots and scope rows. Under the 2024 ruler they")
    print("are added to the 2025 count. Under the 2025 ruler they are removed")
    print("from the 2024 base. The 2025 ruler row is exact for COTS, because the")
    print("2024 rows are known. The 2024 ruler row is a floor: it adds back the")
    print("2024 commercial uses, but commercial uses that began in 2025 sit in")
    print("the grid with no use case records and cannot be counted.")


if __name__ == "__main__":
    main()

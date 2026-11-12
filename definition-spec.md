# Definition spec: Federal AI Inventory Restatement

Version 1.0, 2026-11-12. Locked when committed to the repo.

This spec fixes every definition and rule the build uses. It is committed to the repo before any classification starts. After it is locked, a change requires a dated entry in the amendment log, and any results produced under the earlier version are rerun.

## 1. Scope

- Transition: the 2024 inventory to the 2025 inventory.
- Unit of analysis: one individually reported use case.
- Agencies: every agency with an individual use case in either year's OMB consolidated file.
- Out of the use case count: the 2025 commercial product grid. It records agency by category certifications, not use cases. It is used only as evidence for the `cots` label.

## 2. Baselines

- Primary 2024 baseline: OMB's revised file, 2,133 use cases.
- Sensitivity baseline: OMB's original file, 1,757 use cases. Every headline growth figure is also reported against it.
- 2025 count: OMB's individually reported file, 3,611 use cases.
- The revised file is primary because it is the complete 2024 inventory. The original file is a December 2024 snapshot missing several agencies.

## 3. Sources of record

- Counts come from the OMB consolidated files.
- Matching uses the agency's own file when it carries identifiers that OMB's file lacks.
- When an agency file and OMB disagree on a count, the difference is reconciled row by row and logged. Neither source is silently preferred.
- Agency files no longer hosted may come from the Internet Archive. The capture URL and date go in the manifest.
- Every source file is committed under data/raw with its URL, retrieval date, size, SHA-256 hash, and encoding in data/raw/manifest.csv.

## 4. Text handling

- Each file is decoded with the encoding recorded in the manifest. Agency files are not assumed to be UTF-8.
- Normalization for all comparisons: Unicode NFKC, curly quotes to straight, en and em dashes to hyphens, whitespace collapsed, lowercase.
- Name key: the normalized name with everything except letters and digits removed.
- Word set: words of three or more characters from the name and description fields, minus a fixed stop list. The stop list is the one in hhs-match.py.

## 5. Matching

Matching links each 2024 use case to its 2025 counterpart, if one exists. Tiers run in order. A use case matched at one tier is not passed to the next.

1. **Identifier.** Both years carry the same agency identifier.
2. **Disclosed rename.** The 2025 name field states the prior name, for example "Renamed: X Previously: Y" or "previously named Y." The prior name is matched against 2024 names by name key.
3. **Exact name.** Same name key, within the same operating division.
4. **Mutual best match.** Within the same operating division, each is the other's highest scoring candidate, with a score of at least 0.6.
5. **Manual review.** Everything left.

Scoring: the higher of name similarity (sequence ratio on name keys) and word overlap (Jaccard on word sets).

Blocking: candidates come from the same operating division. When a division has no rows in the other year, or the 2024 entry is filed at department level, the whole agency is the pool.

Matching error: DOJ's identifier-matched pairs give the calibration. Text matching alone finds the true partner 86 percent of the time at best. Misclassification runs from about 14 percent at a 0.5 threshold to about 26 percent at 0.9. These rates are carried into the range for agencies without identifiers.

## 6. Labels for 2024 use cases

Every 2024 use case gets exactly one label. When more than one could apply, the first in this list wins.

| Label | Rule |
|---|---|
| `retired` | The agency's own 2024 stage is retired. No other evidence qualifies. |
| `continues` | Matched one to one, at tier 1, 3, or 4, with the same or nearly the same name. |
| `renamed` | Matched one to one, under a new identifier or a clearly different name. Includes tier 2. |
| `merged` | The matched 2025 entry also carries another 2024 entry, or several 2024 entries point to one 2025 entry. |
| `cots` | No individual 2025 entry, the use is a listed commercial product use, and the agency certified a matching 2025 grid category as in use. |
| `scope` | No individual 2025 entry, and either the 2024 entry states the AI is unused or not AI, or its 2024 commercial category has no 2025 equivalent. |
| `gone` | Active in 2024, no 2025 counterpart, and no documented reason. |
| `unsure` | Still unresolved after review against the full agency 2025 list. |

Rules settled by the pilots:

- An active use case that vanished is `gone`, even when it probably ended. Only the agency's own disclosure makes it `retired`.
- A merge target is often an entry that already continues an older use case. Manual review uses the full agency 2025 list, never a list of new entries alone.
- An agency that filed no 2025 grid cannot produce a `cots` label. Its vanished commercial uses are `gone`.
- A 2025 identifier reused for a different use case is logged as a persistence violation and treated as unmatched.

Commercial category alignment between 2024 and 2025 follows the crosswalk in the brief: matched, reworded, 2024 only, and 2025 only.

## 7. Categories for 2025 use cases

- `continuation`: the counterpart of a 2024 use case labeled continues, renamed, or merged.
- `new`: no 2024 counterpart.
- `retired, traced`: marked retired and matched to a 2024 entry.
- `retired, backfilled`: marked retired, absent from 2024, present in 2023.
- `retired, untraced`: marked retired with no match in 2024 or 2023.
- `duplicate`: a second row for the same use case. Removed before any growth figure.

## 8. Rulesets

The headline is a range across two rulesets. They differ only on judgment calls.

| Judgment call | Strict ruleset | Loose ruleset |
|---|---|---|
| Matching threshold for review candidates | 0.5 | 0.8 |
| `unsure` rows | Counted as continuations | Counted as gone, and the 2025 candidate as new |
| Reworded commercial categories | Counted as `cots` | Counted as `gone` |
| Placeholder entries consolidated into one 2025 entry | `merged` | `merged` |

Strict minimizes genuine new use cases. Loose maximizes them.

## 9. Rulers

- **2024 ruler:** the 2025 count restated at 2024 granularity and scope. Merged, cots, and scope rows are added to the 2025 count.
- **2025 ruler:** the 2024 count restated at 2025 granularity and scope. The same rows are removed from the 2024 base.
- For the commercial component, the 2025 ruler is exact. The 2024 ruler is a floor, because commercial uses that began in 2025 have no use case records.
- The research and development scope change is not observable in either year's data. It is reported as unmeasured, with any agency statements quoted.
- The gap between rulers that comes from applying the same adjustments to two different bases is arithmetic. It is not reported as a finding.

## 10. Headline metrics

- Published growth, against both 2024 baselines.
- Growth with duplicates removed.
- Growth under each ruler, under each ruleset. Four figures, reported as a range.
- Continuity rate: 2024 use cases that continue in some form.
- Disappearance rate: share of 2024 use cases labeled gone. Aggregate only.
- Verified residual rate, from section 12.
- Gross turnover: new 2025 entries and vanished 2024 entries, next to net growth.

## 11. Sampling

- Agencies with 60 or fewer review rows: every row is reviewed.
- Larger agencies: every commercial-flagged review row, plus a random sample of 40 from the rest.
- Seed: 20261111 for every agency.
- Sample counts are scaled to the pool with a finite population correction and reported with a 95 percent range.

## 12. Verification

- **Blind check.** Before the full build, a second rater labels a random 50 review rows with no proposals visible. Agreement and Cohen's kappa are reported. The full build proceeds only at 80 percent agreement or higher. Below that, the label rules are tightened and the check is rerun.
- **Automatic match spot check.** A random 30 of the exact and mutual matches are reviewed, seed 20261111. More than 5 percent wrong pairs, meaning two or more of 30, triggers a review of every automatic match.
- **Residual check.** A random 50 entries classified as new under the loose ruleset are confirmed against agency records, including prior inventories and public descriptions. The verified rate is reported next to the range.

## 13. Publication rules

- Disappearance results are published as aggregate rates only. No agency or tool is named as having removed a use case.
- Per agency detail stays in results/, which is excluded from the public repo.
- The crosswalk dataset is published with its matches. Gone labels appear only as totals in aggregate tables, never at row level.

## Amendment log

| Date | Version | Change |
|---|---|---|
| 2026-11-12 | 0.1 | Draft from DOJ and HHS pilots. |
| 2026-11-12 | 1.0 | Decisions settled: revised baseline primary, 80 percent blind check bar, 5 percent spot check trigger, gone labels aggregate only. Locked. |

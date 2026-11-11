# Federal AI Inventory Restatement

One line: test how much of the reported growth in federal AI use cases survives a constant definition restatement. OMB changed its own reporting rules mid series, and the resulting counts are still cited as an adoption trend.

Status: revised after scoring. Changes are listed in the revision log at the end.

## Origin and fit

This runs on the measurement fragility thesis, not the transfer thesis. It is the second study in the lane opened by Federal AI Spend Audit. That study found that headline federal AI counts shift 19 percent based solely on keyword list width.

The portfolio reason for choosing this lane: seven of the published research pieces are talent portability in sports, and that lane is near saturation. The AI and systems group holds four items. Three are tools and only one is a research finding. This study adds a second finding to the underbuilt lane that matches the working domain.

## Research question

Primary: decompose the year over year change in reported federal AI use cases between the 2024 and 2025 inventories into its component causes. Report what share of the published change survives restatement under a constant definition.

Components are signed. A rule or composition change can inflate or deflate the published figure, so restated growth can be larger or smaller than published growth.

The headline is a range, not a point. It is computed under two or more explicit classification rulesets. See the analyst discretion section.

Restatement runs in both directions where the data allows. Restate the earlier year under the newer rules. Restate the later year under the older rules. If the two restatements disagree about the size of the change, the choice of ruler is itself load bearing, and that disagreement is the finding.

Both directions depend on the field crosswalk check. If the 2024 records lack the fields the M-25-21 scope rule needs, the newer ruler cannot be applied to the earlier year. In that case the study runs the direction the data supports and states the limit plainly.

## Conventional wisdom under test

Inventory growth is read as adoption growth. Published counts are quoted as a barometer of federal AI uptake. The claim under test is that the reported change differs materially from the real change in AI use because of reporting rule changes, agency composition changes, and recategorization. The difference can run in either direction.

Numbers in circulation that this speaks to: roughly 700 use cases in the 2023 consolidated list against 2,133 publicly reportable use cases across 41 agencies in 2024. A GAO cut of 12 selected agencies reported 1,110 use cases in 2024 against 571 the prior year, with generative AI use cases at 282 against 32.

## Self-differentiation risk, stated up front

The obvious objection is that Federal AI Spend Audit already showed a federal AI headline moving on definition choice. A second study concluding the same thing adds little.

The defense rests on what each study targets.

- Spend Audit tested sensitivity on a hypothetical. It showed how a count would move if an analyst chose a different keyword list. No published trend rested on that list.
- This study tests a number already in circulation. The inventory counts are quoted as an adoption trend. OMB changed the reporting rules between years while that trend kept being cited.

Spend Audit showed the scale is sensitive. This study checks whether a specific published reading is wrong.

The mechanism difference supports this but cannot carry it alone. Described by mechanism, both studies reduce to the same takeaway: the federal AI number moves on definition. The target is what separates them.

This should be scored on whether that distinction holds, not assumed to hold.

## Analyst discretion inside the method

The decomposition assigns every changed record to one of five buckets. Each assignment is an analyst judgment. A reworded entry could be a recategorization or a genuine new use case. A DHS commercial off the shelf consolidation could be a scope change or a composition change. Reasonable analysts will split these differently.

Spend Audit found that analyst discretion moves a federal AI headline by 19 percent. A single point estimate here would carry the same weakness this study sets out to measure.

The response is to make discretion part of the method.

- Run the full decomposition under at least two classification rulesets, strict and loose. A middle ruleset is optional.
- Strict: a record counts as genuine new only when it has no plausible prior year match by identifier or by description, and no documented rule or composition explanation applies.
- Loose: a record counts as genuine new whenever its identifier is new and no documented rule or composition change applies.
- Report the headline as a range across rulesets.

Target headline form: under every classification ruleset tested, the share of reported growth that is genuine falls between X and Y.

Exact ruleset text is locked in the definition spec before any classification starts.

## Residual verification

Genuine new use cases are the residual. Four buckets are positively identified: composition, scope, retirement, and disappearance. Genuine growth is what is left over, and it is also the headline.

A residual absorbs all classification error in the exercise. That error does not cancel. A systematic tendency to under-assign scope changes inflates genuine growth in one direction.

Mitigation: draw a random sample of 50 entries classified as genuine new under the loose ruleset. Confirm each against the agency record, including historical inventory versions and public descriptions. Report the verified rate alongside the range. This converts the residual from an assumption into a measured quantity.

## Differentiation scan result

Two passes. First pass on 2026-09-03. Second pass on 2026-09-16, targeted at GAO, inspector general, and CRS products, plus the think tanks that analyze the inventories.

Verdict: the gap is open. No source separates published growth into genuine new use cases versus rule and composition artifacts. None restates the series under a constant definition. This is the differentiated shape.

Covered by others:

- Narrative, per agency coverage of removals. FedScoop reports State Department removals including a behavioral analytics system, with OMB declining to comment on the removals or on guidance about deleting items. FedScoop also reports DHS deleting its entry for a TSA use case called AskTSA, and ICE moving its license plate capture and analysis tool back to pilot while removing the high impact risk management information.
- Aggregate growth counts and stage breakdowns. GAO has published use case totals, generative AI totals, and deployment stage shares.
- Anecdotal acknowledgment of rule effects. In its generative AI report, GAO notes that DOE and NASA officials attributed a year over year drop to a clarified research and development definition in the 2024 guidance. This is a footnote, not a measurement.
- Agency level inventory quality audits. GAO found IRS lacked a comprehensive quality assurance process for inventory entries as of June 2025. GAO found SBA did not consistently meet reporting requirements and published its first inventory in March 2026. Neither addresses the governmentwide trend.
- No inspector general or CRS product on inventory comparability surfaced.

Closest adjacent work:

- Brookings, April 2026. Matched more than 1,000 use cases across the 2024 and 2025 inventories by agency and name. The match was used only to track risk designation changes. The report says some growth likely reflects guidance changes but does not quantify it. This is the nearest competitor, and the author already has matching infrastructure.
- CDT, April 2026. Argues the roughly 70 percent increase likely understates AI use, because the new consolidated commercial off the shelf category moves common commercial tool use out of the individual count. Not quantified.

New evidence for the thesis:

- Published growth figures for the same transition already disagree. Nextgov reported 105 percent growth against a 2024 base of 1,757. Brookings and CDT reported roughly 69 to 70 percent against a base of 2,133. The 1,757 figure was a December 2024 snapshot across 37 agencies. Same 2025 count, two growth rates, from baseline choice alone.

Design signals for the pilot:

- Rule effects may run in both directions. CDT's argument implies the COTS change deflated the individual count. Artifacts cannot be assumed to only inflate growth.
- Identifier coverage is weaker than the brief assumed. Brookings reports that several 2025 agency inventories, including Education, HHS, State, and GSA, did not include unique use case IDs, and Treasury ID conventions vary by office. It also reports that OMB's consolidated 2023 and 2024 lists excluded IDs. Renamed use cases also defeat name matching.
- The field crosswalk may cut the other way. OMB reduced the number of questions for 2025. Dropped fields could block restating 2025 under the older rules. The new COTS category has no 2024 equivalent field.

Residual risk: Brookings extends its match into a growth decomposition, or GAO issues a governmentwide review of the 2025 inventories. No in-progress GAO product was found.

## Scope decision

Narrow. The 2024 to 2025 transition only.

Reason: this is the single transition where the governing guidance changed, which makes it the cleanest natural experiment. The full 2022 to 2025 panel offers more data, but the early years are messier and less consolidated.

## Measurement approach

Decompose the year over year change into mutually exclusive categories:

- Genuine new use cases. Computed as the residual and verified by sample.
- Agency composition change. Agencies entering or exiting reporting. The 2024 inventory covered 41 agencies. The 2025 repository reflects 56 total agency submissions, which include individually reported use cases, consolidated commercial off the shelf entries, or confirmation that AI is not in use. That mix needs unpacking before the counts are comparable.
- Scope and rule changes. OMB amended the scope for reporting AI research and development use cases to align to M-25-21. Recategorization also occurred at agency level, for example DHS moving most common commercial AI use cases into a separate reporting category.
- Disclosed retirements. Use cases marked retired under the OMB instruction.
- Unexplained disappearances. Entries that vanish with no retirement record. Published as an aggregate only. See the framing section.

Headline output: share of published change that survives constant definition restatement. Reported as a range across classification rulesets, under each ruler the data supports, with the verified residual rate alongside.

## Definition spec

Lock before analysis. Definition drift is the known failure mode.

- Use case identity: the OMB unique use case identifier. OMB instructs that retired use cases must be reported as such in the inventory immediately following the year the use case was last operational. After that, the identifier must not be repeated. This persistence rule is the load bearing assumption for matching. It is an instruction to agencies, not a guarantee, and the identifier pilot measures how well it holds.
- Retired: present in the inventory with a retired status.
- Disappeared: identifier present in the prior year, absent in the current year, with no retired record.
- In scope: pin one scope rule per ruler and hold it. The two rulers are the prior guidance scope and the M-25-21 scope.
- Commercial off the shelf entries: decide inclusion explicitly, since consolidated COTS reporting is a category that moved.
- Classification rulesets: strict and loose rules written out in full, with worked examples for reworded entries and COTS consolidations.
- Verification sample: sample size, draw method, and what counts as confirmation against the agency record.

## Sample picture

No rare cell problem at the top line. Thousands of use cases across both years. This inverts the constraint that governed the NHL PTO study.

One cell may be rare and is flagged for the n-count gate: unexplained disappearances. Sketched, not counted. If that cell is small, it stays a secondary observation and no framing should lean on it.

All counts above are from published sources. The decomposition shares are not yet counted.

## Feasibility checks

Two checks run together before the build depends on either.

Pilot sequence: DOJ first, then HHS as a second increment once DOJ verifies. DOJ publishes identifiers, so it tests matching under good conditions. HHS did not publish identifiers in 2025, so it tests the fallback matching key. The first DOJ check reproduces DOJ's published counts before any matching: 240 use cases in the OMB 2024 file, and 315 in 2025, which DOJ reports as a 30.7 percent increase.

Identifier stability pilot. Measure what share of prior year identifiers can be matched into the current year. Agencies have deleted entries outright rather than marking them retired, so identifier discipline is likely uneven. The match rate is reported as a finding whatever it shows. A low rate is a disclosure integrity result on its own and is publishable in short form. That gives the study a floor if the full decomposition fails.

Field crosswalk check. Compare the fields in the 2024 records against what the M-25-21 scope rule requires. This determines whether bidirectional restatement is available. The disagreement between rulers is the sharpest possible result, so this check protects the most important claim in the design.

## Data findings from source pull

Recorded 2026-11-03. These come from the OMB consolidated files only. No agency files read yet.

Baselines:

- Both 2024 baselines are OMB files in the same repo. The original file holds 1,757 rows. The revised v2 file holds 2,133 rows. The commit adding v2 says 376 use cases were added. The two circulating growth rates trace to which file each outlet used.
- 2025 individually reported file holds 3,611 rows, matching OMB's published count.

Encoding:

- 2024 original: UTF-8. 2024 v2: Windows-1252. 2025 files: UTF-8.
- Text matching requires per-file decoding, then normalization of quotes, non-breaking spaces, and whitespace. Some fields contain run-together words, so exact string matching is not a safe key.

Schema:

- 2024 original and v2 share a 62-column layout. Labels differ: coded names in the original, question text in v2. Columns align by position.
- 2025 has 36 columns.
- The 2024 consolidated files carry no use case identifier. OMB's 2024 data dictionary starts at field 2 under its identifier section. ID matching needs agency-hosted 2024 files for every agency.
- The 2025 file carries an id column, but coverage is uneven. HHS (447 rows), State (60), TVA (59), and Education (56) have no ids. HHS is the largest agency in 2025.

Stage:

- 2024 stage values: Initiated, Acquisition and/or Development, Implementation and Assessment, Operation and Maintenance, Retired, plus several nonstandard values. 2025 values: Pre-deployment, Pilot, Deployed, Retired. A stage crosswalk is needed. Retired exists in both.
- Retired rows are inside both published totals: 142 in 2024 v2, 314 in 2025. 2025 also has 338 rows with blank stage.

Commercial product reporting:

- The 2025 COTS file is an agency by category grid, not a list of use cases. 900 rows: 45 agencies by 20 categories. Each row certifies use or non-use. It cannot be counted alongside use cases.
- 2024 field 10 flags use cases implemented solely with a listed commercial product. 436 of 2,133 rows carry a listed category. Two carry off-list text. 47 are blank.
- Category alignment between the 2024 list and the 2025 grid:
  - Matched or near-identical: 11 categories, 155 flagged 2024 rows.
  - Reworded in 2025, scope changed: 4 categories, 225 rows. Includes searching for information, the largest 2024 category at 177 rows.
  - Present in 2024 only: 3 categories, 56 rows.
  - New in 2025 only: 4 categories, including document drafting and code generation. 2024 rows that would fall here were not flagged and need text classification.

Restatement feasibility:

- 2024 under 2025 rules: feasible for the COTS change by dropping flagged rows. Reworded categories map onto the strict and loose rulesets. The four new categories need text classification, which adds analyst discretion.
- 2025 under 2024 rules: not feasible for the COTS change. Uses moved into the grid have no individual record to add back.
- R&D scope change: not observable in either file, since excluded R&D was never reported. Estimable only from agency notes.
- Bidirectional restatement holds for some components only. The headline must say which components were restated in which direction.

Preliminary arithmetic, not findings:

- Excluding retired rows from both years moves published growth from 69.3 percent to 65.6 percent.
- If every flagged 2024 commercial use left individual reporting in 2025, the restated 2024 base falls. Matched categories only: growth of about 83 percent. Matched plus reworded: about 106 percent.
- Both bounds assume flagged uses vanished from the 2025 individual file. The DOJ pilot shows this fails for at least one large agency. Treat both figures as upper bounds, not estimates.
- Direction: the COTS rule change likely deflated published growth. This supports the signed decomposition.

## DOJ pilot results

Completed 2026-11-11. First increment of the identifier stability pilot. Per agency detail, including tool names, stays in results/ and out of the public repo.

Reconciliation:

- DOJ's own 2024 file has 241 rows. One is a placeholder recorded as removed for administrative error. OMB dropped it. DOJ had 240 real use cases, and OMB's count is correct.
- OMB's 2025 file has 314 DOJ rows but 312 distinct ids. Two use cases are listed twice. Published DOJ growth overstates by 2.

Identifiers:

- 79.2 percent of 2024 ids reappear in 2025 (190 of 240).
- 90.0 percent of 2024 use cases continue in some form once merges and renames are counted (216 of 240).
- 8 use cases continue under a new id. Each one breaks OMB's rule that identifiers persist.
- 59 of 191 id-matched pairs changed name. 17 changed substantially. A recurring pattern: a named product in 2024 became a generic function label in 2025.

2024 side decomposition:

| Outcome | Count | Share |
|---|---|---|
| Continues by id | 190 | 79.2% |
| Merged into another entry | 18 | 7.5% |
| Renamed under a new id | 8 | 3.3% |
| Retired, disclosed | 8 | 3.3% |
| Gone, no counterpart | 16 | 6.7% |

Restatement:

| Measure | 2024 base | 2025 count | Growth |
|---|---|---|---|
| Published | 240 | 314 | 30.8% |
| Duplicates removed | 240 | 312 | 30.0% |
| 2024 ruler | 240 | 330 | 37.5% |
| 2025 ruler | 222 | 312 | 40.5% |

- Under either constant ruler, DOJ growth runs 7 to 10 points above published. Consolidation shrank the 2025 count.
- The gap between the two rulers is arithmetic, not a finding. Both rows use the same 18 merges. A ruler disagreement counts as a finding only when the rulers adjust different components.

Commercial product reporting:

- DOJ is not in the 2025 COTS grid. Neither are several other agencies with individual use cases. The grid is a partial roster, which makes it a composition issue.
- DOJ flagged 18 uses as commercial in 2024. 14 continue in the 2025 individual file. DOJ kept reporting commercial tools one by one, so the COTS rule barely affected its growth.
- DOJ left its 2024 commercial flag blank on 223 of 241 rows. A blank does not mean non-commercial.

Disappearance cell:

- 16 of 240, or 6.7 percent. Too small to stand alone for one agency. Workable as an aggregate rate across agencies.

Matcher calibration, for agencies without identifiers:

- Text matching alone finds the true 2025 partner 86 percent of the time at best. The true partner is in the top 3 candidates 93 percent of the time.
- Misclassification runs from about 14 percent at a low threshold to about 26 percent at a high one. No threshold does better than 14 percent.
- At the low threshold, errors are wrong pairings. At high thresholds, errors are missed matches, which count as one disappearance plus one new entry.
- The threshold is the ruleset knob. Low maps to strict, high maps to loose. Each ruleset now carries a measured error rate.
- Calibrated on DOJ only. HHS may describe use cases differently.

Method notes for the definition spec:

- Labels: continues, merged, renamed, retired, gone, scope, cots, unsure.
- Retired requires the agency's own retired status. An active use case that vanished is gone, even when it probably ended.
- A 2025 entry that already carries a 2024 id makes any second 2024 match a merge, not a rename.
- Manual review needs the full agency 2025 list. A partial list of new ids hides every merge target.
- Label agreement was 39 of 50, but the review was guided by proposals. It is not inter-rater evidence. A blind second rater is needed for that, best done on HHS.

## Complexity

This is the largest build in the portfolio. It involves dozens of agency CSVs with different schemas across two years, thousands of records, manual classification under multiple rulesets, a verification sample, and up to two ruler passes. Plan it as a multi week build.

The offset is the artifact, described below.

## Artifact assessment

One falls out naturally. A year over year crosswalk of the inventories, with the constant definition restatement, is a dataset others could apply to their own questions. It is a byproduct of the method rather than a bolt on. The classification rules served the same role for Federal AI Spend Audit.

The crosswalk is published as a dataset with the study.

This is the first study in the queue where the artifact check returns yes without forcing.

## Framing constraint

The most vivid disappearance examples involve the State Department, DHS, and ICE. A count of undisclosed removals reads as a political finding regardless of the framing sentence around it, because the removals are the story and the agencies are named in the data.

Decision: publish the disappearance count as an aggregate disclosure compliance rate. No per agency naming in the published findings. The measurement claim survives intact.

Fallback, either or: if the aggregate still reads as an agency story in review, fold disappearances into a general unmatched category and keep the study strictly on the ruler change.

## Timing

Hold for the second differentiation pass, then publish once the analysis holds. The 2025 inventory is already released, so there is no data wait. GAO is the live risk, and one pass is not enough against an audit body that publishes on this subject.

## Data sources

- OMB consolidated 2025 federal agency AI use case inventory repository on GitHub.
- Agency hosted machine readable CSV inventories, linked from the OMB data sourcing summary.
- Prior year agency inventories, including agency inventory libraries that retain 2022 through 2024 versions.
- OMB reporting instructions and guidance memoranda for the scope rules under each ruler.
- GAO reporting for published totals and cross checks.
- Internet Archive captures of agency files no longer hosted, such as DOJ's 2024 inventory. Used only when the OMB consolidated file lacks identifiers. Capture URL and date are logged.

Source handling:

- Both OMB repositories are cloned with full history, since OMB processes updates on a rolling basis.
- Raw source files are committed to the public repo as snapshots. A manifest records the URL, retrieval date, and file hash for each file.
- Pilot outputs stay out of the public repo. Per agency match and disappearance results are not published before framing review.

All live data runs locally, not in a sandbox.

## Gates remaining before build

In order, cheapest first:

1. Second differentiation pass against GAO and inspector general products. Complete on 2026-09-16. Gap open.
2. Identifier stability pilot, with the field crosswalk check attached. DOJ complete on 2026-11-11. HHS next.
3. N-count gate on the unexplained disappearance cell, using pilot agencies.
4. Definition spec locked in writing, including classification rulesets and the verification sample.
5. Continuation gate on the pilot evidence: continue to build, convert to the short form match rate finding, or archive.

## Revision log

- Title set: Federal AI Inventory Restatement.
- Self-differentiation defense rebuilt on target rather than mechanism.
- Added analyst discretion section. Headline is now a range across classification rulesets.
- Added residual verification sample.
- Added field crosswalk check. Bidirectional restatement is now conditional on it.
- Identifier match rate is now reported as a finding and sets a short form floor.
- Framing constraint resolved to aggregate disappearance reporting, with a fallback.
- Added complexity section. Crosswalk is published as a dataset.
- Timing resolved to hold for the second differentiation pass.
- Gates reordered cheapest first, with the continuation gate added.
- Decomposition made signed. Artifacts can inflate or deflate published growth.
- Pilot sequence set: DOJ first, then HHS. First check reproduces DOJ's published counts.
- Source handling set: full history clones, committed raw snapshots with a manifest, archive captures allowed with provenance, pilot outputs kept out of the public repo.
- Second differentiation pass complete. Gap confirmed open. Added adjacent work, the conflicting published growth rates, and three design signals for the pilot.
- Added data findings from the source pull.
- Added DOJ pilot results. The governmentwide COTS figures are now labeled upper bounds. The ruler gap is reframed as arithmetic.

<!-- sources
OMB 2025 consolidated inventory repository, identifier persistence and retirement instruction, 56 agency submissions: https://github.com/ombegov/2025-Federal-Agency-AI-Use-Case-Inventory
FedScoop, 2024 inventory total 2,133 across 41 agencies and roughly 700 in 2023: https://fedscoop.com/us-government-annual-tally-ai-use-cases-coming-soon/
FedScoop, DHS updated inventory, AskTSA deletion, ICE license plate reversion: https://fedscoop.com/dhs-updated-ai-inventory-risk-management-high-impact/
FedScoop, State Department removals and OMB declining comment: https://fedscoop.com/state-department-removes-several-ai-uses/
GAO figures via The Register, 1,110 vs 571 use cases and 282 vs 32 generative AI: https://www.theregister.com/2025/07/29/us_government_identified_ai_use/
DHS inventory library, historical versions and COTS recategorization: https://www.dhs.gov/publication/ai-use-case-inventory-library
DOJ AI inventory, M-25-21 reference: https://www.justice.gov/ai/ai-inventory
GAO-25-107653, DOE and NASA R&D definition footnote: https://files.gao.gov/reports/GAO-25-107653/index.html
GAO-26-107522, IRS inventory quality assurance: https://files.gao.gov/reports/GAO-26-107522/index.html
GAO-26-107828, SBA inventory reporting: https://www.gao.gov/products/gao-26-107828
Brookings, 2024 to 2025 matching, missing identifiers, 69 percent growth: https://www.brookings.edu/articles/assessing-the-state-of-ai-adoption-across-the-federal-government/
CDT, COTS consolidation may understate growth: https://cdt.org/insights/one-year-retrospective-on-the-federal-governments-implementation-of-updated-ai-guidance-accelerating-usage-with-incomplete-safeguards/
Nextgov, 105 percent growth against 1,757 base: https://www.nextgov.com/artificial-intelligence/2026/04/agencies-report-over-3000-ai-use-cases-2025/412898/
FedScoop, December 2024 snapshot of 1,757 across 37 agencies: https://fedscoop.com/federal-government-discloses-more-than-1700-ai-use-cases/
OMB 2024 consolidated inventory repository: https://github.com/ombegov/2024-Federal-AI-Use-Case-Inventory
-->


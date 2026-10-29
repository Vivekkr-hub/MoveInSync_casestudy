# MoveInSync Play Store review analysis and tracker

**Forward Deployed Engineer assignment | Vivek Kumar | 29 October 2026**

This project investigates recurring complaints in public Google Play reviews, recommends practical fixes, and provides a repeatable tracker for the question: **“How are our Play Store ratings?”**

## Start here

Read [the recommendations](MoveInSync_Recommendations_Vivek_Kumar.pdf) for priorities, engineering actions, acceptance criteria, owners, and a 60-day delivery plan. Keep the separately supplied PDF beside this README in the project root; No dashboard is included in this package.

**Recommendation:** prioritize reliable login and self-booking, keep optional feedback from blocking essential trip tasks, and establish an accountable complaint-resolution process. Investigate safety reports immediately, regardless of frequency. Reviews identify symptoms; internal telemetry and reproduction are needed to confirm causes.

### Baseline findings

Analysis window: **1 November 2025–29 October 2026, inclusive**. “Low-rated” means **1–2 stars** throughout this README.

| Measure | Result |
| --- | --- |
| Employee-app store snapshot | 4.64 / 5 from 115,574 ratings |
| Downloaded reviews within the analysis window | 2,758 |
| Mean rating in that review sample | 3.84 / 5 |
| Low-rated reviews | 746 (27.05%) |
| Low-rated reviews with a developer reply | 24 / 746 (3.22%) |
| Leading report themes | Stability: 137; tracking/trip information: 89; login/OTP: 83; booking: 77 |

The store score and review-sample average cover different populations and periods. Their difference does not establish a historical decline. Themes overlap, and reply presence does not establish resolution.

## Quick start: reproduce the submission

Extract the ZIP into a folder, preserving the `data/`, `labels/`, `validation/`, and `out/` directories. Open a terminal in that folder. Use Python 3.10 or newer as a recommended environment; no minimum-version compatibility matrix has been tested.

The offline workflow uses the Python standard library and bundled files. It needs neither internet access nor an AI API key:

```bash
python tracker.py --offline --as-of 2026-10-29
```

Expected headline output: **2,758 reviews, 746 low-rated reviews, and 3.22% reply coverage**. The raw average is rounded to three decimal places in the tracker and two in the PDF.

The command prints the baseline and investigation alerts, then writes:

- `out/metrics.json`: store snapshots, review summaries, peer summaries, monthly and version breakdowns, provisional keyword themes, and alerts.
- `out/reviews_tagged.csv`: low-rated employee-app reviews in the reporting window, with provisional keyword tags.

These outputs are overwritten on each run. Preserve the supplied dataset before a live refresh if you want to reproduce this exact submission later. `--as-of` filters currently stored records; it cannot restore earlier versions of edited reviews.

### Rebuild the supporting report outputs

Run these commands against the supplied data:

```bash
python analyze_reviews.py
python analyze_trends.py
python finalize_labels.py
```

They rebuild `out/baseline_summary.json`, `out/monthly_trends.csv`, `out/version_trends.csv`, `out/report_labels.json`, and `out/report_theme_summary.json`. These scripts use the fixed submission window, not a rolling reporting date. They do not regenerate the PDF or call an AI model.

## Refresh or monitor ratings

For live collection, install the scraper dependency:

```bash
python -m pip install google-play-scraper
python tracker.py
```

A live run snapshots six app listings and refreshes review datasets for MoveInSync employee, Safetrax Commuter, and Routematic. It fetches available review pages, merges by review ID, and updates existing review text and replies. It is **not a new-reviews-only download**. Previously stored reviews absent from a refresh are retained.

To analyze stored data using today's India date without making network requests:

```bash
python tracker.py --offline
```

The tracker uses a window beginning on the first day of the month 11 months before the reporting month and ending on the reporting date. `--as-of` is supported only with `--offline`.

For an individual dataset refresh:

```bash
python fetch_reviews.py com.moveinsync.ets data/ets_en.jsonl en in
```

Check the exit status and collection metadata before using refreshed results. A failed tracker run may leave outputs from an earlier run; successful earlier collection steps may already have updated their files.

### Investigation alerts

| Signal | Current rule |
| --- | --- |
| Keyword spike | At least 5 low-rated matches in the last 7 days and at least twice the prior 8-week weekly average; also flags when that prior count is zero |
| Safety triage | Any safety keyword match in low-rated reviews from the last 7 days |
| Version investigation | Any version in the reporting window with at least 30 reviews and more than 30% one-star reviews |
| Reply coverage | Fewer than 90% of low-rated reviews from the last 30 days have a nonempty developer reply |
| Collection freshness | Metadata missing, collection not exhausted, or collection older than 7 days |
| Snapshot freshness | An available store snapshot is older than 7 days |

These are investigation signals, not confirmed defects or release regressions. Suggested use: weekly and after releases, with a person reviewing matching text and assigning follow-up. **Scheduling and notifications are not installed.**

## How the evidence was produced

Collection used `google-play-scraper`, newest-first pagination, `lang=en`, and `country=in`. The supplied datasets contain 24,431 MoveInSync, 1,652 Safetrax, and 7,226 Routematic unique review IDs. Collection metadata records timing and completion status. Pagination exhaustion means the scraper returned no more pages, not that every public review was captured. Reviewer names and profile images are removed; review text and audit IDs remain.

Two separate classification methods serve different purposes:

| Method | Purpose and source |
| --- | --- |
| Report labels | Fixed recommendation evidence in `out/report_labels.json`: 725 original unverified AI labels, 20 second AI-assisted checks, and 1 additional AI-assisted label |
| Keyword tags | Repeatable monitoring through `themes.py`; written to tracker outputs and treated as provisional |

The second AI-assisted check agreed exactly with the original theme sets on 16 of 20 records. This measures agreement, **not accuracy or independent human validation**. Despite its filename, `manual_check_20.csv` contains an AI-assisted check. The finalized report uses the copy under `validation/`. Multi-label counts must not be summed as unique affected users.

Claude supplied initial scripts and labels. ChatGPT assisted with debugging, analysis, the second check, and report preparation. Python was run in VS Code, and sample labels were transferred through Excel. This README was subsequently revised with ChatGPT and its documented offline commands checked against the supplied files.

## File guide

| File or directory | Role |
| --- | --- |
| `tracker.py` | Current live/offline monitoring entry point |
| `fetch_reviews.py` | Review collection, updates, retry handling, and metadata |
| `themes.py` | Provisional keyword rules and suggested owners |
| `analyze_reviews.py` | Fixed-window baseline and basic data checks |
| `analyze_trends.py` | Fixed-window monthly and version summaries |
| `finalize_labels.py` | Reconciles original labels and checked records for the report |
| `data/*.jsonl`, `data/*.meta.json` | Stored reviews and collection provenance |
| `data/snapshots.csv` | Store scores, counts, and star histograms |
| `data/app_meta.json`, `data/competitor_meta.json` | Supporting listing metadata |
| `labels/` | Original AI labels and labeling instructions |
| `validation/` | Earlier sample comparisons and the second 20-record check |
| `out/` | Generated summaries, report labels, tagged reviews, and audit files |
| `analyze_themes.py`, `prepare_label_check.py` | Intermediate audit/sample preparation; not required to reproduce the final report outputs |
| `tracker old.py`, `report_data.py` | Legacy scripts; not part of the supported workflow above |

`report_data.py` requires pandas and an absent input, `data/most_relevant_en_in.json`. It references an earlier dashboard workflow and should not be used to reproduce this submission. Earlier validation and provisional theme files are retained for provenance; the final report themes are in `out/report_theme_summary.json`.

## Verification and limits

The documented fixed-date tracker run and three supporting report commands were rerun successfully against a scratch copy of the supplied archive during this README update. The tracker reproduced 2,758 reviews, 746 low-rated reviews, and 3.22% reply coverage. Live collection was not rerun during this update; the combined live refresh remains unverified end-to-end in this review.

- Written reviews are self-selected and do not measure the proportion of all users affected. English/India request parameters do not establish reviewer residence or complete geographic coverage. iOS is outside scope.
- Review dates are used as supplied; their timezone is unspecified, and reviews may be edited. Historical as-of reporting is not an immutable archive.
- Snapshot differences are **net changes** that may include additions, edits, removals, and source corrections, not a distribution of new ratings.
- Nine MoveInSync developer replies predate the current review timestamps. A nonempty reply may not address the current complaint.
- Most report labels remain unverified. Keyword tags may misread negation, praise, and ambiguous text. Neither method establishes technical root causes.
- Peer comparisons are descriptive; different clients, users, sample sizes, and review practices prevent a controlled ranking.
- October is partial, version information is missing for 271 of 2,758 records, and small version samples require caution.

Public sources: [MoveInSync employee](https://play.google.com/store/apps/details?id=com.moveinsync.ets), [Safetrax Commuter](https://play.google.com/store/apps/details?id=in.mtap.iincube.safetrax.commuter), and [Routematic](https://play.google.com/store/apps/details?id=com.routematic.employee).

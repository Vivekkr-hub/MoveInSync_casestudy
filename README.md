# MoveInSync: review evidence and ratings tracker

**Vivek Kumar — Forward Deployed Engineer case study**  
Collection date: **29 October 2026**. Fixed reporting window: **1 November 2025–29 October 2026**.

## Start here

Read [the recommendation PDF](MoveInSync_Recommendations_Vivek_Kumar.pdf) for the proposed priorities, owners, delivery sequence and success checks. This repository contains supporting evidence and a repeatable monitoring workflow. It does not implement fixes inside MoveInSync or claim access to internal telemetry.

| Baseline | Result |
| --- | ---: |
| Downloaded MoveInSync records, all dates | 24,431 |
| Records in the reporting window | 2,758 |
| Mean stars in that review sample | 3.841 |
| 1–2-star records | 746 (27.05%) |
| Low-rated records with any developer reply | 24 (3.22%) |
| Replies predating the current review timestamp | 9 |

The supplied store snapshot reports approximately **4.64/5**. That score and the sample mean describe different populations and periods. Their difference does not demonstrate a historical decline. Public reviews identify symptoms and investigation priorities, not confirmed causes or prevalence across all employees.

## Quick start: reproduce offline

Clone or download this repository, then open its folder in VS Code and open a terminal. Python 3.10+ is recommended.

```bash
git clone https://github.com/Vivekkr-hub/MoveInSync_casestudy.git
cd MoveInSync_casestudy
```

 The final analysis scripts and offline tracker use only the standard library; no API key or package installation is needed for these commands.

```bash
python analyze_reviews.py
python analyze_trends.py
python finalize_labels.py
python tracker.py --offline --as-of 2026-10-29
```

Expected tracker results include `reviews: 2758`, `low_rated: 746`, `avg: 3.841`, and `reply_coverage_percent: 3.22`. Investigation alerts are expected; they are not execution errors. The four commands were run successfully against the packaged data during final review.

The scripts regenerate JSON/CSV outputs, not the designed PDF. Preserve this submission folder before refreshing live data if you need an unchanged baseline.

## Refresh public data

Only live collection requires `google-play-scraper==1.2.7`, pinned in `requirements.txt`. The version below is the version shown in the candidate's successful installation.

```bash
python -m pip install -r requirements.txt
python tracker.py
```

The live tracker appends snapshots for the employee, driver and field apps plus two peers, then refreshes the three employee-app review datasets. It stops on a collection failure; existing outputs may then be from an earlier run. The downloader completed successfully on the candidate's Windows machine for all three apps. The combined live tracker has **not** been verified end-to-end.

To refresh just the employee reviews:

```bash
python fetch_reviews.py com.moveinsync.ets data/ets_en.jsonl en in
```

The downloader paginates newest-first, retries requests, merges records by review ID and refreshes retrieved edits/replies. It retains previously stored records absent from a later run. `exhausted` means no further scraper pages, not proof of complete coverage. Metadata records collection time and status. Ctrl+C is handled by saving collected results; a forced process termination is different.

To analyze stored data relative to today's India date:

```bash
python tracker.py --offline
```

`--as-of` requires `--offline`. It filters the current stored records by date; it cannot reconstruct historical versions of edited reviews. The fixed-report analysis scripts retain their submission dates and do not automatically become rolling reports.

## File guide

| File or folder | Purpose |
| --- | --- |
| `tracker.py` | Rolling monitor: snapshot context, peers, monthly/version summaries, provisional keyword signals and freshness warnings |
| `fetch_reviews.py` | Public review collection and refresh; writes JSONL plus collection metadata |
| `themes.py` | Original keyword taxonomy; provisional matches, not validated root causes |
| `analyze_reviews.py` | Fixed-window data checks and peer baseline |
| `analyze_trends.py` | Fixed-window monthly and exact-version summaries; flags samples under 30 |
| `finalize_labels.py` | Joins original AI labels to current text, applies the checked sample and labels the extra trip-feedback record |
| `analyze_themes.py` | Intermediate audit of original AI labels; not the final report counts |
| `prepare_label_check.py` | Reproduces the 20-record sample; refuses to overwrite an existing sample file |
| `data/*.jsonl`, `data/*.meta.json` | Freshly collected reviews and collection metadata |
| `data/snapshots.csv` | Timestamped store snapshot inherited from the supplied project; live tracker appends new observations |
| `data/app_meta.json`, `data/competitor_meta.json` | Original project metadata; not refreshed by the revised tracker |
| `labels/labeled.json`, `labels/instructions.md` | Original AI labels and taxonomy instructions; preserved for provenance |
| `validation/manual_check_20.csv` | Second AI-assisted check, despite the historical filename; not a human gold standard |
| Other `validation/` files | Inherited model/rule comparisons; not independently validated accuracy results |
| `out/baseline_summary.json` | Fixed-window peer summary |
| `out/monthly_trends.csv`, `out/version_trends.csv` | Fixed-window trend tables |
| `out/report_labels.json`, `out/report_theme_summary.json` | Consolidated AI-assisted evidence used in the report |
| `out/metrics.json` | Tracker results, collection freshness, limitations and alerts |
| `out/reviews_tagged.csv` | Low-rated reviews in the tracker window with provisional keyword tags |
| `out/theme_audit.csv`, `out/theme_summary_provisional.json` | Intermediate original-label audit; superseded for report use by consolidated outputs |

If retained in the repository, `tracker old.py` and `report_data.py` are legacy files; use the commands above for the final analysis. Do not upload your local virtual environment.

## Two classification methods: do not mix them

**Report:** 746 low-rated records; 725 original unverified AI labels, 20 second-pass AI-assisted classifications and one additional trip-feedback label. Final counts include stability 137, tracking 89, login/OTP 83, booking 77 and repeated/blocking prompts 48. Multiple labels are possible, so counts cannot be added as unique users. The second check agreed exactly on 16/20 label sets. That is agreement, not 80% accuracy. Ambiguous cases remain, and the sample does not establish population accuracy.

**Monitor:** regex matching in `themes.py`. It can misclassify praise, negation, vague language and words used in a different context. Owner mappings are routing suggestions. Inspect the source text before action, particularly safety signals. Keyword counts can differ from the report's AI-label counts.

## Monitoring rules and proposed cadence

- Run weekly and after app releases; scheduling is not installed.
- Investigate a keyword with at least five low-rated mentions in seven days and at least twice its previous eight-week weekly average (including a zero baseline).
- Inspect versions with at least 30 reviews and more than 30% one-star reviews in the reporting window. This is an association, not a causal regression test.
- Reply presence below a proposed 90% threshold triggers a queue review; it does not measure timely acknowledgement or resolution.
- Collections and available store snapshots older than seven days are flagged. Missing collection metadata is flagged. Read freshness warnings before interpreting alerts.
- Histogram changes between the last two snapshots are **net changes**, potentially affected by edits, removals and source corrections. They are not the distribution or average of new ratings.

## Sources and limitations

Collection requested English reviews from the India storefront:

- [MoveInSync employee](https://play.google.com/store/apps/details?id=com.moveinsync.ets&hl=en&gl=IN)
- [Safetrax Commuter](https://play.google.com/store/apps/details?id=in.mtap.iincube.safetrax.commuter&hl=en&gl=IN)
- [Routematic](https://play.google.com/store/apps/details?id=com.routematic.employee&hl=en&gl=IN)

These settings do not establish reviewer residence or guarantee every returned text is English. Reviews are self-selected. Peer samples differ substantially (2,758 / 110 / 690 in the window), and their users and client contexts are not controlled. Dates are used as supplied, with unspecified review timezone. October is partial. 271 MoveInSync records lack version information. One collected record has empty text. No duplicate/missing review IDs, missing dates or invalid star scores were found in the collected files.

Reply coverage counts any nonempty reply. Old replies can remain after an edited review. No response-time or resolution claim follows from coverage alone. Snapshot counts and downloaded review counts are separate source measures. No promised star-rating uplift is inferred from complaint counts.

## Tools, contribution and validation

Claude supplied initial code and AI labels. ChatGPT assisted with code corrections, analysis, a second AI-assisted sample check, consolidation, documentation and recommendation drafting. The candidate collected data and ran scripts in VS Code; Excel was used to transfer the sample classifications. There is no independent human label-validation claim.

Final offline checks reproduced the baseline, consolidated label counts, monthly totals and missing-version count. Earlier tracker checks covered empty summaries and stale-data warnings. Live scraping depends on an unofficial library and upstream responses; the combined live refresh remains unverified. The proposed product fixes require internal investigation, tests and controlled rollout.

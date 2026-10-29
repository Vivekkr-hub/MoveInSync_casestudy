import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

with (ROOT / "data" / "ets_en.jsonl").open(encoding="utf-8") as file:
    reviews = [json.loads(line) for line in file if line.strip()]

with (ROOT / "labels" / "labeled.json").open(encoding="utf-8") as file:
    labels = {
        row["reviewId"]: row
        for row in json.load(file)
    }

negative = [
    row for row in reviews
    if "2025-11-01" <= row["at"][:10] < "2026-10-30"
    and row["score"] <= 2
]

counts = Counter()
audit = []
matched = 0

for review in negative:
    old = labels.get(review["reviewId"])

    unchanged = (
        old is not None
        and old.get("content") == review.get("content")
        and old.get("score") == review.get("score")
    )

    if unchanged:
        themes = sorted(set(old.get("t", [])))
        issue = old.get("issue", "")
        status = "existing_ai_label_unverified"
        matched += 1
        counts.update(themes)
    else:
        themes = []
        issue = ""
        status = "needs_label"

    audit.append({
        "review_id": review["reviewId"],
        "date": review["at"],
        "stars": review["score"],
        "review_text": review.get("content", ""),
        "ai_themes": ";".join(themes),
        "ai_issue": issue,
        "label_status": status,
        "checked_themes": "",
        "reviewer_notes": "",
    })

audit.sort(key=lambda row: row["date"], reverse=True)

with (OUT / "theme_audit.csv").open(
    "w", newline="", encoding="utf-8-sig"
) as file:
    writer = csv.DictWriter(file, fieldnames=list(audit[0]))
    writer.writeheader()
    writer.writerows(audit)

summary = [
    {
        "theme": theme,
        "reviews_tagged": count,
        "percent_of_all_low_rated_reviews": round(
            100 * count / len(negative), 2
        ),
    }
    for theme, count in counts.most_common()
]

with (OUT / "theme_summary_provisional.json").open(
    "w", encoding="utf-8"
) as file:
    json.dump({
        "low_rated_reviews": len(negative),
        "matched_existing_labels": matched,
        "needs_label": len(negative) - matched,
        "classification": "Existing AI labels, not yet manually validated",
        "themes": summary,
    }, file, indent=2)

print(f"Low-rated reviews: {len(negative)}")
print(f"Matched existing labels: {matched}")
print(f"Needs labeling: {len(negative) - matched}")

print("\nPROVISIONAL theme counts:")
for item in summary:
    print(f"{item['theme']}: {item['reviews_tagged']}")

print("\nSaved: out/theme_audit.csv")
print("Saved: out/theme_summary_provisional.json")
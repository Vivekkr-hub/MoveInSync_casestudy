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
    original = {row["reviewId"]: row for row in json.load(file)}

with (ROOT / "validation" / "manual_check_20.csv").open(
    encoding="utf-8-sig", newline=""
) as file:
    checked = {row["review_id"]: row for row in csv.DictReader(file)}

results = []
counts = Counter()

for review in reviews:
    if not (
        "2025-11-01" <= review["at"][:10] < "2026-10-30"
        and review["score"] <= 2
    ):
        continue

    review_id = review["reviewId"]
    old = original.get(review_id)
    check = checked.get(review_id)

    if check and check["review_text"] == review.get("content"):
        themes = [
            value.strip()
            for value in check["checked_themes"].split(";")
            if value.strip()
        ]
        source = "second_ai_assisted_check"
        note = check.get("reviewer_notes", "")

    elif (
        old
        and old.get("content") == review.get("content")
        and old.get("score") == review["score"]
    ):
        themes = old["t"]
        source = "original_ai_label_unverified"
        note = old.get("issue", "")

    elif (
        review_id == "34148866-4305-4445-83ef-ba60b37cd29c"
        and review.get("content")
        == "i am unable to rate any of my trips just useless"
    ):
        themes = ["trip_feedback"]
        source = "additional_ai_assisted_label"
        note = "Cannot submit trip ratings; not a forced-rating complaint."

    else:
        themes = ["unclear"]
        source = "needs_review"
        note = "No matching label for the current review text."

    themes = sorted(set(themes))
    counts.update(themes)

    results.append({
        "review_id": review_id,
        "date": review["at"],
        "stars": review["score"],
        "review_text": review.get("content", ""),
        "themes": themes,
        "label_source": source,
        "note": note,
    })

with (OUT / "report_labels.json").open("w", encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)

summary = {
    "reviews": len(results),
    "method": "AI-assisted classification; not human-validated",
    "multi_label": True,
    "label_sources": dict(Counter(row["label_source"] for row in results)),
    "themes": [
        {
            "theme": theme,
            "count": count,
            "percent_of_low_rated_reviews": round(
                100 * count / len(results), 2
            ),
        }
        for theme, count in counts.most_common()
    ],
}

with (OUT / "report_theme_summary.json").open(
    "w", encoding="utf-8"
) as file:
    json.dump(summary, file, indent=2)

print(json.dumps(summary, indent=2))
print("\nSaved out/report_labels.json and out/report_theme_summary.json")
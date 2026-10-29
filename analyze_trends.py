import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

with (ROOT / "data" / "ets_en.jsonl").open(encoding="utf-8") as file:
    reviews = [json.loads(line) for line in file if line.strip()]

recent = [
    review for review in reviews
    if "2025-11-01" <= review["at"][:10] < "2026-10-30"
]


def summarize(group):
    total = len(group)
    low = [review for review in group if review["score"] <= 2]

    return {
        "reviews": total,
        "average_stars": round(
            sum(review["score"] for review in group) / total, 3
        ),
        "low_rated_reviews": len(low),
        "low_rated_percent": round(100 * len(low) / total, 2),
        "one_star_percent": round(
            100 * sum(review["score"] == 1 for review in group) / total,
            2,
        ),
    }


monthly = defaultdict(list)
versions = defaultdict(list)
missing_version = 0

for review in recent:
    monthly[review["at"][:7]].append(review)

    version = review.get("reviewCreatedVersion")
    if version:
        versions[str(version)].append(review)
    else:
        missing_version += 1

monthly_rows = [
    {
        "month": month,
        **summarize(group),
        "partial_month": month == "2026-10",
    }
    for month, group in sorted(monthly.items())
]

version_rows = [
    {
        "version": version,
        **summarize(group),
        "first_review_in_window": min(r["at"] for r in group),
        "last_review_in_window": max(r["at"] for r in group),
        "small_sample": len(group) < 30,
    }
    for version, group in sorted(versions.items())
]


def save_csv(filename, rows):
    if not rows:
        return

    with (OUT / filename).open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


save_csv("monthly_trends.csv", monthly_rows)
save_csv("version_trends.csv", version_rows)

print("MONTHLY RESULTS")
for row in monthly_rows:
    suffix = " (partial month)" if row["partial_month"] else ""
    print(
        f"{row['month']}: {row['reviews']} reviews | "
        f"average {row['average_stars']} | "
        f"1-2 stars {row['low_rated_percent']}%{suffix}"
    )

print(f"\nReviews missing version information: {missing_version}")
print("Saved: out/monthly_trends.csv")
print("Saved: out/version_trends.csv")
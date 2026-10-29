import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / "out" / "theme_audit.csv"
target = ROOT / "out" / "manual_check_20.csv"

with source.open(encoding="utf-8-sig", newline="") as file:
    rows = list(csv.DictReader(file))

# Fixed seed makes the sample reproducible.
sample = random.Random(42).sample(rows, min(20, len(rows)))

# Hide AI labels so your judgment starts with the review itself.
fields = [
    "review_id",
    "date",
    "stars",
    "review_text",
    "checked_themes",
    "reviewer_notes",
]

if target.exists():
    raise SystemExit(
        "manual_check_20.csv already exists. Keeping your existing work."
    )

with target.open("w", encoding="utf-8-sig", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for row in sample:
        writer.writerow({field: row.get(field, "") for field in fields})

print("Saved: out/manual_check_20.csv")
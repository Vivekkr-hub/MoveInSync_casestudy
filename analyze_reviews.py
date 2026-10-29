import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START = "2025-11-01"
END = "2026-10-30"  # Exclusive: includes October 29

APPS = {
    "MoveInSync": "ets_en.jsonl",
    "Safetrax": "safetrax_en.jsonl",
    "Routematic": "routematic_en.jsonl",
}

results = []

for name, filename in APPS.items():
    path = ROOT / "data" / filename

    with path.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]

    ids = [row.get("reviewId") for row in rows]

    if any(not review_id for review_id in ids):
        raise ValueError(f"{name}: missing review IDs")

    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: duplicate review IDs")

    if any(row.get("score") not in [1, 2, 3, 4, 5] for row in rows):
        raise ValueError(f"{name}: invalid star ratings")

    if any(not row.get("at") for row in rows):
        raise ValueError(f"{name}: missing dates")

    recent = [
        row for row in rows
        if START <= row["at"][:10] < END
    ]

    negative = [row for row in recent if row["score"] <= 2]

    replied = sum(
        bool((row.get("replyContent") or "").strip())
        for row in negative
    )

    result = {
        "app": name,
        "total_downloaded": len(rows),
        "period_start": START,
        "period_end_exclusive": END,
        "recent_review_records": len(recent),
        "average_review_rating": (
            round(sum(row["score"] for row in recent) / len(recent), 3)
            if recent else None
        ),
        "low_rated_reviews": len(negative),
        "low_rated_reviews_with_reply": replied,
        "reply_coverage_percent": (
            round(100 * replied / len(negative), 2)
            if negative else None
        ),
        "empty_text_records": sum(
            not (row.get("content") or "").strip() for row in rows
        ),
    }

    results.append(result)
    print(json.dumps(result, indent=2))

output = ROOT / "out"
output.mkdir(exist_ok=True)

with (output / "baseline_summary.json").open("w", encoding="utf-8") as file:
    json.dump(results, file, indent=2)

print("\nSaved: out/baseline_summary.json")
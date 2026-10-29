"""Download and refresh Google Play reviews.

Usage:
    python fetch_reviews.py APP_ID OUTPUT_FILE [LANG] [COUNTRY]

Each run fetches the reviews available through the scraper.
Existing records are updated by review ID, including developer replies.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from google_play_scraper import Sort, reviews


def save_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
    os.replace(temporary, path)


def main():
    if len(sys.argv) < 3:
        raise SystemExit(
            "Usage: python fetch_reviews.py APP_ID OUTPUT_FILE [LANG] [COUNTRY]"
        )

    app_id = sys.argv[1]
    output = Path(sys.argv[2])
    lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    country = sys.argv[4] if len(sys.argv) > 4 else "in"

    output.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()

    records = {}
    if output.exists():
        with output.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    record = json.loads(line)
                    records[record["reviewId"]] = record

    existing_ids = set(records)
    fetched_ids = set()
    token = None
    status = "running"
    error = None
    page = 0

    try:
        while True:
            for attempt in range(4):
                try:
                    batch, next_token = reviews(
                        app_id,
                        lang=lang,
                        country=country,
                        sort=Sort.NEWEST,
                        count=200,
                        continuation_token=token,
                    )
                    break
                except Exception:
                    if attempt == 3:
                        raise
                    wait = 2 ** (attempt + 1)
                    print(f"Request failed; retrying in {wait} seconds...")
                    time.sleep(wait)

            if not batch:
                status = "exhausted"
                break

            page += 1
            unseen_this_page = 0
            fetched_at = datetime.now(timezone.utc).isoformat()

            for review in batch:
                record = dict(review)
                review_id = record["reviewId"]

                if review_id not in fetched_ids:
                    unseen_this_page += 1

                fetched_ids.add(review_id)

                for field in ("at", "repliedAt"):
                    value = record.get(field)
                    record[field] = value.isoformat() if value else None

                # Reviewer names and photos aren't needed for this analysis.
                record.pop("userName", None)
                record.pop("userImage", None)

                record["app_id"] = app_id
                record["requested_lang"] = lang
                record["requested_country"] = country
                record["fetched_at_utc"] = fetched_at

                records[review_id] = record

            print(
                f"Page {page}: {len(fetched_ids)} unique reviews retrieved",
                flush=True,
            )

            if next_token is None or not getattr(next_token, "token", None):
                status = "exhausted"
                break

            if unseen_this_page == 0:
                status = "stopped_repeated_page"
                break

            token = next_token
            time.sleep(0.5)

    except KeyboardInterrupt:
        status = "interrupted"
        error = "Stopped by user; collected records were saved."

    except Exception as exc:
        status = "failed"
        error = str(exc)

    # Write safely: replace the original only after writing finishes.
    ordered = sorted(
        records.values(),
        key=lambda record: record.get("at") or "",
        reverse=True,
    )

    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as file:
        for record in ordered:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    os.replace(temporary, output)

    metadata = {
        "app_id": app_id,
        "requested_lang": lang,
        "requested_country": country,
        "started_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "unique_reviews_fetched_this_run": len(fetched_ids),
        "new_review_ids": len(fetched_ids - existing_ids),
        "total_stored_reviews": len(records),
        "error": error,
        "note": (
            "Exhausted means the scraper returned no further pages, "
            "not proof that every Play review was retrieved. "
            "Previously stored reviews absent from this run are retained."
        ),
    }
    save_json(output.with_suffix(".meta.json"), metadata)

    print(f"\nStatus: {status}")
    print(f"Fetched this run: {len(fetched_ids)}")
    print(f"Total stored: {len(records)}")
    print(f"Saved to: {output}")

    if error:
        print(f"Details: {error}")

    if status != "exhausted":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
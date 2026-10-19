import json
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import Sort, reviews


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "apps_metadata_unified.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

REVIEWS_FILE = OUTPUT_DIR / "apps_reviews.csv"
FAILURES_FILE = OUTPUT_DIR / "apps_reviews_failed.csv"
PROGRESS_FILE = OUTPUT_DIR / "apps_reviews_progress.json"

# Keep the test small until the improved collector is verified.
MAX_APPS = None
REVIEWS_PER_APP = 100

LANGUAGE = "en"
COUNTRY = "in"
REQUEST_DELAY = 1.0


# --------------------------------------------------
# File helpers
# --------------------------------------------------

def load_json(path, default):
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    temporary_path.replace(path)


def load_existing_reviews():
    if not REVIEWS_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(REVIEWS_FILE)

    if "reviewId" not in df.columns or "app_id" not in df.columns:
        raise ValueError(
            "Existing reviews file must contain reviewId and app_id. "
            "Inspect the file before continuing."
        )

    return df


def save_reviews(new_reviews):
    """Save reviews while preserving existing records."""
    if not new_reviews:
        return

    new_df = pd.DataFrame(new_reviews)

    if REVIEWS_FILE.exists():
        existing_df = pd.read_csv(REVIEWS_FILE)

        combined = pd.concat(
            [existing_df, new_df],
            ignore_index=True,
            sort=False,
        )
    else:
        combined = new_df

    # Review IDs are the primary duplicate key.
    combined = combined.drop_duplicates(
        subset=["reviewId"],
        keep="first",
    )

    combined.to_csv(REVIEWS_FILE, index=False)


def save_failures(failures):
    if failures:
        pd.DataFrame(failures).to_csv(FAILURES_FILE, index=False)
    elif FAILURES_FILE.exists():
        FAILURES_FILE.unlink()


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input dataset not found: {INPUT_FILE}")

    apps_df = pd.read_csv(INPUT_FILE)

    required_columns = {"app_id", "app_name"}

    if not required_columns.issubset(apps_df.columns):
        raise ValueError(
            f"Input dataset must contain: {required_columns}"
        )

    apps_df = apps_df.dropna(subset=["app_id"]).copy()
    apps_df["app_id"] = apps_df["app_id"].astype(str).str.strip()
    apps_df = apps_df[apps_df["app_id"] != ""]
    apps_df = apps_df.drop_duplicates(subset=["app_id"])

    # Load existing review data and progress.
    existing_reviews = load_existing_reviews()
    progress = load_json(PROGRESS_FILE, {"apps": {}})
    app_progress = progress.setdefault("apps", {})

    # Backward compatibility: recognize apps already collected in the
    # original test, even though no progress file existed then.
    if not existing_reviews.empty:
        for app_id, group in existing_reviews.groupby("app_id"):
            app_id = str(app_id)

            if app_id not in app_progress:
                app_progress[app_id] = {
                    "status": (
                        "completed"
                        if len(group) >= REVIEWS_PER_APP
                        else "partial"
                    ),
                    "reviews_saved": int(len(group)),
                    "note": "Recovered from existing review CSV",
                }

    # Only skip apps explicitly marked completed or no_reviews.
    # Failed and partial apps remain eligible for another attempt.
    completed_statuses = {"completed", "no_reviews"}

    apps_to_process = apps_df[
        ~apps_df["app_id"].isin(
            [
                app_id
                for app_id, record in app_progress.items()
                if record.get("status") in completed_statuses
            ]
        )
    ]

    if MAX_APPS is not None:
        apps_to_process = apps_to_process.head(MAX_APPS)

    print(f"Apps in unified dataset: {len(apps_df)}")
    print(f"Previously tracked apps: {len(app_progress)}")
    print(f"Apps selected for this run: {len(apps_to_process)}")
    print(f"Maximum reviews per app: {REVIEWS_PER_APP}")
    print(f"Existing reviews: {len(existing_reviews)}")
    print(f"Output: {REVIEWS_FILE}")

    failures = []

    if FAILURES_FILE.exists():
        old_failures = pd.read_csv(FAILURES_FILE)
        failures = old_failures.to_dict("records")

    for index, (_, row) in enumerate(
        apps_to_process.iterrows(),
        start=1,
    ):
        app_id = str(row["app_id"])
        app_name = str(row.get("app_name", ""))

        print(
            f"\n[{index}/{len(apps_to_process)}] "
            f"{app_name} ({app_id})"
        )

        try:
            result, continuation_token = reviews(
                app_id,
                lang=LANGUAGE,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=REVIEWS_PER_APP,
            )

            for review in result:
                review["app_id"] = app_id
                review["app_name"] = app_name

            save_reviews(result)

            # Record a terminal status for this app.
            # An app with fewer than the requested number of reviews
            # is still complete for this collection pass.
            status = "completed" if result else "no_reviews"

            app_progress[app_id] = {
                "status": status,
                "app_name": app_name,
                "reviews_returned": len(result),
                "last_attempt": time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "more_reviews_available": bool(continuation_token),
            }

            # Remove stale failure entries after a successful attempt.
            failures = [
                failure
                for failure in failures
                if str(failure.get("app_id")) != app_id
            ]

            print(f"Reviews returned: {len(result)}")

            if continuation_token:
                print("Additional reviews may be available.")

        except Exception as exc:
            print(f"Failed: {exc}")

            app_progress[app_id] = {
                "status": "failed",
                "app_name": app_name,
                "error": str(exc),
                "last_attempt": time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }

            failures = [
                failure
                for failure in failures
                if str(failure.get("app_id")) != app_id
            ]

            failures.append(
                {
                    "app_id": app_id,
                    "app_name": app_name,
                    "error": str(exc),
                }
            )

        finally:
            # Persist progress after every app.
            save_json(PROGRESS_FILE, progress)
            save_failures(failures)
            time.sleep(REQUEST_DELAY)

    print("\nCollection run finished.")
    print(f"Progress file: {PROGRESS_FILE}")

    if REVIEWS_FILE.exists():
        final_df = pd.read_csv(REVIEWS_FILE)
        print(f"Total saved reviews: {len(final_df)}")
        print(f"Apps represented: {final_df['app_id'].nunique()}")

    status_counts = {}

    for record in app_progress.values():
        status = record.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"Progress summary: {status_counts}")

    if failures:
        print(f"Apps with recorded failures: {len(failures)}")


if __name__ == "__main__":
    main()
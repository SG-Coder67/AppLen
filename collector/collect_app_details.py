import time
from pathlib import Path

import pandas as pd
from google_play_scraper import app


INPUT_PATH = Path("data/raw/apps_discovered.csv")
OUTPUT_PATH = Path("data/raw/apps_details.csv")
FAILED_PATH = Path("data/raw/apps_details_failed.csv")

REQUEST_DELAY = 1


def collect_app_details():
    discovered = pd.read_csv(INPUT_PATH)

    if OUTPUT_PATH.exists():
        existing = pd.read_csv(OUTPUT_PATH)
        completed_ids = set(existing["app_id"].dropna().astype(str))
        records = existing.to_dict("records")
    else:
        completed_ids = set()
        records = []

    pending = discovered[
        ~discovered["app_id"].astype(str).isin(completed_ids)
    ]

    print(f"Discovered apps: {len(discovered)}")
    print(f"Already collected: {len(completed_ids)}")
    print(f"Remaining: {len(pending)}")

    failures = []

    for position, (_, row) in enumerate(pending.iterrows(), start=1):
        app_id = str(row["app_id"])

        print(f"[{position}/{len(pending)}] Fetching {app_id}...")

        try:
            details = app(
                app_id,
                lang="en",
                country="in",
            )
            record = {
                "app_id": details.get("appId"),
                "app_name": details.get("title"),
                "discovery_category": row["category"],
                "store_category": details.get("genre"),
                "developer": details.get("developer"),
                "rating": details.get("score"),
                "rating_count": details.get("ratings"),
                "installs": details.get("installs"),
                "min_installs": details.get("minInstalls"),
                "real_installs": details.get("realInstalls"),
                "price": details.get("price"),
                "currency": details.get("currency"),
                "is_free_download": details.get("free"),
                "offers_in_app_purchases": details.get("offersIAP"),
                "in_app_product_price": details.get("inAppProductPrice"),
                "contains_ads": details.get("containsAds"),
                "description": details.get("description"),
                "summary": details.get("summary"),
                "content_rating": details.get("contentRating"),
                "released": details.get("released"),
                "last_updated": details.get("lastUpdatedOn"),
                "version": details.get("version"),
                "developer_website": details.get("developerWebsite"),
                "developer_email": details.get("developerEmail"),
                "app_url": details.get("url"),
                "country": "IN",
            }

            records.append(record)
            completed_ids.add(app_id)

            # Save immediately so successful work is preserved.
            pd.DataFrame(records).drop_duplicates(
                subset="app_id",
                keep="last",
            ).to_csv(OUTPUT_PATH, index=False)

        except Exception as error:
            print(f"  Failed: {error}")

            failures.append({
                "app_id": app_id,
                "app_name": row["app_name"],
                "error": str(error),
            })

        time.sleep(REQUEST_DELAY)

    if failures:
        failed_df = pd.DataFrame(failures)

        if FAILED_PATH.exists():
            previous = pd.read_csv(FAILED_PATH)
            failed_df = pd.concat(
                [previous, failed_df],
                ignore_index=True,
            )

        failed_df.drop_duplicates(
            subset="app_id",
            keep="last",
        ).to_csv(FAILED_PATH, index=False)

    print("\nCollection finished.")
    print(f"Successfully collected: {len(completed_ids)}")
    print(f"Saved to: {OUTPUT_PATH}")

    if FAILED_PATH.exists():
        print(f"Failed-app log: {FAILED_PATH}")


if __name__ == "__main__":
    collect_app_details()
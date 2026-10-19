import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

REVIEWS_FILE = BASE_DIR / "data/raw/apps_reviews.csv"
METADATA_FILE = BASE_DIR / "data/processed/apps_metadata_unified.csv"
PROGRESS_FILE = BASE_DIR / "data/raw/apps_reviews_progress.json"
REPORT_FILE = BASE_DIR / "data/processed/apps_reviews_validation_report.txt"

reviews = pd.read_csv(REVIEWS_FILE)
metadata = pd.read_csv(METADATA_FILE)

with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
    progress = json.load(f)

# Basic integrity checks
total_reviews = len(reviews)
unique_review_ids = reviews["reviewId"].nunique()
duplicate_review_ids = reviews["reviewId"].duplicated().sum()

missing_content = reviews["content"].isna().sum()
empty_content = (
    reviews["content"].fillna("").astype(str).str.strip().eq("").sum()
)
missing_scores = reviews["score"].isna().sum()

invalid_scores = (
    ~reviews["score"].dropna().between(1, 5)
).sum()

represented_apps = reviews["app_id"].nunique()
metadata_apps = metadata["app_id"].nunique()

review_counts = reviews.groupby("app_id").size()
apps_with_100_reviews = int((review_counts >= 100).sum())

progress_summary = {}
if isinstance(progress, dict):
    records = progress.get("apps", progress)
    if isinstance(records, dict):
        for record in records.values():
            if isinstance(record, dict):
                status = record.get("status", "unknown")
                progress_summary[status] = (
                    progress_summary.get(status, 0) + 1
                )

# Apps in metadata without any collected reviews
reviewed_ids = set(reviews["app_id"].dropna().astype(str))
metadata_ids = set(metadata["app_id"].dropna().astype(str))
unrepresented_ids = metadata_ids - reviewed_ids

report = f"""
APP REVIEW VALIDATION REPORT
============================

Total reviews: {total_reviews}
Unique review IDs: {unique_review_ids}
Duplicate review IDs: {duplicate_review_ids}

Missing review content: {missing_content}
Empty review content: {empty_content}
Missing ratings: {missing_scores}
Ratings outside 1-5: {invalid_scores}

Apps in metadata: {metadata_apps}
Apps represented in reviews: {represented_apps}
Apps with at least 100 reviews: {apps_with_100_reviews}
Metadata apps without reviews: {len(unrepresented_ids)}

Progress status summary:
{progress_summary}
"""

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
REPORT_FILE.write_text(report.strip() + "\n", encoding="utf-8")

print(report)
print(f"\nReport saved to: {REPORT_FILE}")

# Save the apps that still need investigation
missing_apps = metadata[metadata["app_id"].astype(str).isin(unrepresented_ids)]
missing_apps.to_csv(
    BASE_DIR / "data/processed/apps_without_reviews.csv",
    index=False
)
print("Apps without reviews saved to data/processed/apps_without_reviews.csv")
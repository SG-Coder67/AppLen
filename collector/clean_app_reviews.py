import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data/raw/apps_reviews.csv"
OUTPUT_FILE = BASE_DIR / "data/processed/apps_reviews_cleaned.csv"
REPORT_FILE = BASE_DIR / "data/processed/apps_reviews_cleaning_report.txt"

# Load original collected reviews
df = pd.read_csv(INPUT_FILE)

original_count = len(df)

# Remove duplicate review IDs
df = df.drop_duplicates(subset=["reviewId"], keep="first").copy()
after_deduplication = len(df)

# Remove missing or empty review text
df["content"] = df["content"].fillna("").astype(str)
df["content"] = df["content"].str.replace(r"\s+", " ", regex=True).str.strip()

df = df[df["content"] != ""].copy()
after_text_cleaning = len(df)

# Normalize app IDs without altering review IDs
df["app_id"] = df["app_id"].astype("string").str.strip()

# Normalize ratings to numeric values
df["score"] = pd.to_numeric(df["score"], errors="coerce")

# Keep valid ratings only
df = df[df["score"].between(1, 5)].copy()
df["score"] = df["score"].astype("int8")

# Parse review timestamps
df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)

# Save cleaned dataset
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

report = f"""
APP REVIEW CLEANING REPORT
==========================

Original reviews: {original_count}
After duplicate removal: {after_deduplication}
After removing empty text: {after_text_cleaning}
Final cleaned reviews: {len(df)}

Reviews removed as duplicate IDs: {original_count - after_deduplication}
Reviews removed for empty text: {after_deduplication - after_text_cleaning}
Reviews removed for invalid ratings: {after_text_cleaning - len(df)}

Unique apps in cleaned dataset: {df['app_id'].nunique()}
Unique review IDs in cleaned dataset: {df['reviewId'].nunique()}
Missing ratings in cleaned dataset: {df['score'].isna().sum()}
"""

REPORT_FILE.write_text(report.strip() + "\n", encoding="utf-8")

print(report)
print(f"\nCleaned data saved to: {OUTPUT_FILE}")
print(f"Report saved to: {REPORT_FILE}")
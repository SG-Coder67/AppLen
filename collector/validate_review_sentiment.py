from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data/processed/apps_reviews_sentiment.csv"
REPORT_FILE = BASE_DIR / "data/processed/sentiment_validation_report.txt"

df = pd.read_csv(INPUT_FILE)

expected = {
    "reviewId",
    "app_id",
    "content",
    "score",
    "sentiment",
    "sentiment_confidence",
}

missing_columns = expected - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

allowed_sentiments = {"positive", "negative"}

invalid_sentiments = (
    ~df["sentiment"].astype(str).str.lower().isin(allowed_sentiments)
).sum()

missing_sentiment = df["sentiment"].isna().sum()
missing_confidence = df["sentiment_confidence"].isna().sum()
invalid_confidence = (
    ~pd.to_numeric(
        df["sentiment_confidence"], errors="coerce"
    ).between(0, 1)
).sum()

duplicate_ids = df["reviewId"].duplicated().sum()

rating_sentiment = pd.crosstab(
    df["score"],
    df["sentiment"],
    normalize="index",
).round(3)

sentiment_distribution = (
    df["sentiment"].value_counts(dropna=False)
)

app_sentiment = (
    df.groupby(["app_id", "sentiment"])
    .size()
    .unstack(fill_value=0)
)

if "positive" not in app_sentiment:
    app_sentiment["positive"] = 0

if "negative" not in app_sentiment:
    app_sentiment["negative"] = 0

app_sentiment["review_count"] = (
    app_sentiment["positive"] + app_sentiment["negative"]
)

app_sentiment["positive_share"] = (
    app_sentiment["positive"] / app_sentiment["review_count"]
)

app_sentiment["negative_share"] = (
    app_sentiment["negative"] / app_sentiment["review_count"]
)

app_sentiment = app_sentiment.reset_index()

app_sentiment.to_csv(
    BASE_DIR / "data/processed/app_sentiment_summary.csv",
    index=False,
)

report = f"""
SENTIMENT VALIDATION REPORT
===========================

Total predictions: {len(df)}
Unique apps: {df['app_id'].nunique()}
Duplicate review IDs: {duplicate_ids}
Missing sentiment predictions: {missing_sentiment}
Invalid sentiment labels: {invalid_sentiments}
Missing confidence scores: {missing_confidence}
Invalid confidence scores: {invalid_confidence}

Sentiment distribution:
{sentiment_distribution.to_string()}

Sentiment proportions within each star rating:
{rating_sentiment.to_string()}

Note:
The model predicts binary sentiment. Agreement with star ratings is a
diagnostic check, not proof that either source is always correct.
"""

REPORT_FILE.write_text(report.strip() + "\n", encoding="utf-8")

print(report)
print(f"\nReport saved to: {REPORT_FILE}")
print("App-level summary saved to data/processed/app_sentiment_summary.csv")
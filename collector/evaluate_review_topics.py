from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

TOPICS_FILE = BASE_DIR / "data/processed/review_topics.csv"
SUMMARY_FILE = BASE_DIR / "data/processed/topic_summary.csv"
OUTPUT_FILE = BASE_DIR / "data/processed/topic_evaluation_report.txt"

reviews = pd.read_csv(TOPICS_FILE)
topics = pd.read_csv(SUMMARY_FILE)

# Exclude BERTopic's outlier cluster for topic-level diagnostics
valid_topics = topics[topics["Topic"] != -1].copy()

# Join topic sizes with sentiment statistics
topic_sentiment = (
    reviews[reviews["topic_id"] != -1]
    .groupby("topic_id")
    .agg(
        review_count=("reviewId", "count"),
        negative_share=("sentiment", lambda s: (s == "negative").mean()),
        average_rating=("score", "mean"),
        app_count=("app_id", "nunique"),
    )
    .reset_index()
    .rename(columns={"topic_id": "Topic"})
)

report = valid_topics.merge(topic_sentiment, on="Topic", how="left")

report["negative_share"] = (report["negative_share"] * 100).round(1)
report["average_rating"] = report["average_rating"].round(2)

report = report.sort_values("review_count", ascending=False)

columns = [
    "Topic",
    "review_count",
    "app_count",
    "negative_share",
    "average_rating",
    "Name",
    "Representation",
]

report[columns].to_csv(
    BASE_DIR / "data/processed/topic_quality_metrics.csv",
    index=False,
)

text = f"""
TOPIC EVALUATION REPORT
=======================

Sample size: {len(reviews)}
Discovered non-outlier topics: {len(valid_topics)}
Outlier reviews: {(reviews['topic_id'] == -1).sum()}
Outlier percentage: {(reviews['topic_id'] == -1).mean() * 100:.2f}%

Largest topics:
{report[columns].head(20).to_string(index=False)}

Topics with the highest negative sentiment (minimum 30 reviews):
{report[report['review_count'] >= 30].sort_values(
    'negative_share', ascending=False
)[columns].head(15).to_string(index=False)}

Saved detailed metrics to:
data/processed/topic_quality_metrics.csv
"""

OUTPUT_FILE.write_text(text.strip() + "\n", encoding="utf-8")

print(text)
print(f"\nReport saved to: {OUTPUT_FILE}")
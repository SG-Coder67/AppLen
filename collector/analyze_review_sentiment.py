import json
from pathlib import Path

import pandas as pd
import torch
from transformers import pipeline

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data/processed/apps_reviews_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "data/processed/apps_reviews_sentiment.csv"
PROGRESS_FILE = BASE_DIR / "data/processed/sentiment_progress.json"

MODEL_NAME = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
BATCH_SIZE = 32
SAVE_EVERY = 1000

# Use Apple's Metal GPU when available
DEVICE = 0 if torch.backends.mps.is_available() else -1

print(f"Loading model: {MODEL_NAME}")
print(f"Device: {'Apple Silicon GPU (MPS)' if DEVICE == 0 else 'CPU'}")

classifier = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    device=DEVICE,
)

reviews = pd.read_csv(INPUT_FILE)
reviews["reviewId"] = reviews["reviewId"].astype(str)

# Resume by review ID, not row position
if OUTPUT_FILE.exists():
    previous = pd.read_csv(OUTPUT_FILE)
    previous["reviewId"] = previous["reviewId"].astype(str)
    processed_ids = set(previous["reviewId"])
    print(f"Previously processed reviews: {len(processed_ids)}")
else:
    previous = pd.DataFrame()
    processed_ids = set()

pending = reviews[~reviews["reviewId"].isin(processed_ids)].copy()

print(f"Total reviews: {len(reviews)}")
print(f"Remaining reviews: {len(pending)}")

if pending.empty:
    print("All reviews already have sentiment predictions.")
    raise SystemExit(0)

# Write each completed chunk immediately
for start in range(0, len(pending), SAVE_EVERY):
    chunk = pending.iloc[start:start + SAVE_EVERY].copy()
    texts = chunk["content"].fillna("").astype(str).tolist()

    predictions = classifier(
        texts,
        batch_size=BATCH_SIZE,
        truncation=True,
        max_length=256,
    )

    chunk["sentiment"] = [
        item["label"].lower() for item in predictions
    ]
    chunk["sentiment_confidence"] = [
        float(item["score"]) for item in predictions
    ]
    chunk["sentiment_model"] = MODEL_NAME

    chunk.to_csv(
        OUTPUT_FILE,
        mode="a",
        header=not OUTPUT_FILE.exists(),
        index=False,
    )

    completed = min(start + len(chunk), len(pending))
    total_completed = len(processed_ids) + completed

    progress = {
        "model": MODEL_NAME,
        "total_reviews": len(reviews),
        "previously_processed": len(processed_ids),
        "newly_processed": completed,
        "total_processed": total_completed,
        "device": "mps" if DEVICE == 0 else "cpu",
    }

    PROGRESS_FILE.write_text(
        json.dumps(progress, indent=2),
        encoding="utf-8",
    )

    print(
        f"Processed this run: {completed:,}/{len(pending):,} | "
        f"Total processed: {total_completed:,}/{len(reviews):,}"
    )

print("\nSentiment analysis completed.")
print(f"Output: {OUTPUT_FILE}")
print(f"Progress: {PROGRESS_FILE}")
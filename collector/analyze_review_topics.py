import json
from pathlib import Path

import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data/processed/apps_reviews_sentiment.csv"
OUTPUT_DIR = BASE_DIR / "data/processed"
TOPICS_FILE = OUTPUT_DIR / "review_topics.csv"
SUMMARY_FILE = OUTPUT_DIR / "topic_summary.csv"
MODEL_DIR = OUTPUT_DIR / "bertopic_model"
PROGRESS_FILE = OUTPUT_DIR / "topic_model_progress.json"

SAMPLE_SIZE = 10_000
RANDOM_STATE = 42

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading sentiment dataset...")
df = pd.read_csv(INPUT_FILE)

# Keep valid review text
df = df.dropna(subset=["content"]).copy()
df["content"] = df["content"].astype(str).str.strip()
df = df[df["content"] != ""].copy()

# Select a reproducible sample across apps
sample = (
    df.groupby("app_id", group_keys=False)
    .apply(
        lambda group: group.sample(
            n=min(len(group), max(1, SAMPLE_SIZE // df["app_id"].nunique())),
            random_state=RANDOM_STATE,
        ),
        include_groups=False,
    )
)

# Preserve app identifiers for the output
sample = df.loc[sample.index].copy()

# If group sampling yields fewer rows than the target, top up from remaining data
if len(sample) < min(SAMPLE_SIZE, len(df)):
    remaining = df.loc[~df.index.isin(sample.index)]
    extra_count = min(SAMPLE_SIZE - len(sample), len(remaining))
    if extra_count > 0:
        extra = remaining.sample(n=extra_count, random_state=RANDOM_STATE)
        sample = pd.concat([sample, extra])

sample = sample.drop_duplicates(subset=["reviewId"]).reset_index(drop=True)

print(f"Reviews available: {len(df):,}")
print(f"Reviews selected for topic modeling: {len(sample):,}")

documents = sample["content"].tolist()

print("Loading embedding model...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

vectorizer_model = CountVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.90,
)

topic_model = BERTopic(
    embedding_model=embedding_model,
    vectorizer_model=vectorizer_model,
    min_topic_size=50,
    calculate_probabilities=False,
    verbose=True,
)

print("Fitting BERTopic model...")
topics, _ = topic_model.fit_transform(documents)

sample["topic_id"] = topics

print("Saving review-topic assignments...")
sample.to_csv(TOPICS_FILE, index=False)

print("Building topic summary...")
summary = topic_model.get_topic_info()
summary.to_csv(SUMMARY_FILE, index=False)

print("Saving trained topic model...")
topic_model.save(
    str(MODEL_DIR),
    serialization="safetensors",
    save_ctfidf=True,
    save_embedding_model="sentence-transformers/all-MiniLM-L6-v2",
)

progress = {
    "input_reviews": len(df),
    "sampled_reviews": len(sample),
    "sample_size_requested": SAMPLE_SIZE,
    "random_state": RANDOM_STATE,
    "topics_found": int(len(set(topics) - {-1})),
    "outlier_reviews": int(sum(topic == -1 for topic in topics)),
    "model": "BERTopic",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
}

PROGRESS_FILE.write_text(json.dumps(progress, indent=2), encoding="utf-8")

print("\nTopic modeling completed.")
print(json.dumps(progress, indent=2))
print(f"Review assignments: {TOPICS_FILE}")
print(f"Topic summary: {SUMMARY_FILE}")
print(f"Saved model: {MODEL_DIR}")
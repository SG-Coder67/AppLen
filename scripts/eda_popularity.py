import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

# -----------------------------
# 1. Basic popularity statistics
# -----------------------------

print("\n===== POPULARITY OVERVIEW =====")

print("Total apps:", len(df))

print("\nDownloads statistics:")
print(df["downloads_numeric"].describe())

print("\nPopularity score statistics:")
print(df["popularity_score"].describe())


# -----------------------------
# 2. Top 10 most popular apps
# -----------------------------

print("\n===== TOP 10 APPS BY POPULARITY =====")

top_apps = (
    df[["app_name", "category", "downloads_numeric", "popularity_score"]]
    .sort_values("popularity_score", ascending=False)
    .head(10)
)

print(top_apps.to_string(index=False))


# -----------------------------
# 3. Average popularity by category
# -----------------------------

print("\n===== POPULARITY BY CATEGORY =====")

category_popularity = (
    df.groupby("category")["popularity_score"]
    .agg(["mean", "median"])
    .sort_values("mean", ascending=False)
)

print(category_popularity)


# -----------------------------
# 4. Plot: popularity by category
# -----------------------------

category_popularity["mean"].sort_values().plot(
    kind="barh",
    figsize=(10, 7)
)

plt.xlabel("Average Popularity Score")
plt.ylabel("Category")
plt.title("Average Popularity Score by Category")
plt.tight_layout()

plt.savefig("data/final/popularity_by_category.png", dpi=300)

plt.show()


# -----------------------------
# 5. Plot: download distribution
# -----------------------------

df["log_downloads"].dropna().plot(
    kind="hist",
    bins=10,
    figsize=(8, 5)
)

plt.xlabel("Log10(Downloads)")
plt.ylabel("Number of Apps")
plt.title("Distribution of App Downloads")
plt.tight_layout()

plt.savefig("data/final/download_distribution.png", dpi=300)

plt.show()
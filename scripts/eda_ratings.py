import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

# -----------------------------
# 1. Rating overview
# -----------------------------

print("\n===== RATING OVERVIEW =====")

print(df["rating"].describe())


# -----------------------------
# 2. Top and bottom rated apps
# -----------------------------

print("\n===== TOP 10 RATED APPS =====")

top_rated = (
    df[["app_name", "category", "rating", "downloads_numeric", "engagement_score"]]
    .dropna(subset=["rating"])
    .sort_values("rating", ascending=False)
    .head(10)
)

print(top_rated.to_string(index=False))


print("\n===== BOTTOM 10 RATED APPS =====")

bottom_rated = (
    df[["app_name", "category", "rating", "downloads_numeric", "engagement_score"]]
    .dropna(subset=["rating"])
    .sort_values("rating", ascending=True)
    .head(10)
)

print(bottom_rated.to_string(index=False))


# -----------------------------
# 3. Rating vs popularity
# -----------------------------

correlation = df[["rating", "popularity_score"]].corr().iloc[0, 1]

print("\n===== RATING VS POPULARITY =====")
print(f"Correlation: {correlation:.4f}")


# -----------------------------
# 4. Engagement overview
# -----------------------------

print("\n===== ENGAGEMENT OVERVIEW =====")

print(df["engagement_score"].describe())


# -----------------------------
# 5. Top engagement apps
# -----------------------------

print("\n===== TOP 10 APPS BY ENGAGEMENT =====")

top_engagement = (
    df[["app_name", "category", "rating", "popularity_score", "engagement_score"]]
    .dropna(subset=["engagement_score"])
    .sort_values("engagement_score", ascending=False)
    .head(10)
)

print(top_engagement.to_string(index=False))


# -----------------------------
# 6. Engagement by category
# -----------------------------

print("\n===== ENGAGEMENT BY CATEGORY =====")

category_engagement = (
    df.groupby("category")["engagement_score"]
    .agg(["mean", "median"])
    .sort_values("mean", ascending=False)
)

print(category_engagement)


# -----------------------------
# 7. Rating vs popularity plot
# -----------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    df["popularity_score"],
    df["rating"]
)

plt.xlabel("Popularity Score")
plt.ylabel("Rating")
plt.title("Rating vs Popularity")

plt.tight_layout()
plt.savefig(
    "data/final/rating_vs_popularity.png",
    dpi=300
)

plt.show()


# -----------------------------
# 8. Engagement by category plot
# -----------------------------

category_engagement["mean"].sort_values().plot(
    kind="barh",
    figsize=(10, 7)
)

plt.xlabel("Average Engagement Score")
plt.ylabel("Category")
plt.title("Average Engagement Score by Category")

plt.tight_layout()
plt.savefig(
    "data/final/engagement_by_category.png",
    dpi=300
)

plt.show()
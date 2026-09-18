import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

# --------------------------------
# 1. Category overview
# --------------------------------

print("\n===== CATEGORY OVERVIEW =====")

category_summary = (
    df.groupby("category")
    .agg(
        app_count=("app_name", "count"),
        avg_rating=("rating", "mean"),
        avg_popularity=("popularity_score", "mean"),
        avg_engagement=("engagement_score", "mean"),
        avg_monthly_price=("normalized_monthly_price", "mean"),
    )
    .sort_values("avg_engagement", ascending=False)
)

print(category_summary.round(2))


# --------------------------------
# 2. Category counts
# --------------------------------

print("\n===== APPS PER CATEGORY =====")

print(
    df["category"]
    .value_counts()
)


# --------------------------------
# 3. Pricing model by category
# --------------------------------

print("\n===== PRICING MODEL BY CATEGORY =====")

pricing_by_category = pd.crosstab(
    df["category"],
    df["pricing_type"]
)

print(pricing_by_category)


# --------------------------------
# 4. Highest engagement categories
# --------------------------------

print("\n===== ENGAGEMENT BY CATEGORY =====")

print(
    category_summary[
        ["app_count", "avg_engagement"]
    ]
    .sort_values(
        "avg_engagement",
        ascending=False
    )
    .round(2)
)


# --------------------------------
# 5. Popularity by category
# --------------------------------

print("\n===== POPULARITY BY CATEGORY =====")

print(
    category_summary[
        ["app_count", "avg_popularity"]
    ]
    .sort_values(
        "avg_popularity",
        ascending=False
    )
    .round(2)
)


# --------------------------------
# 6. Rating by category
# --------------------------------

print("\n===== RATING BY CATEGORY =====")

print(
    category_summary[
        ["app_count", "avg_rating"]
    ]
    .sort_values(
        "avg_rating",
        ascending=False
    )
    .round(2)
)


# --------------------------------
# 7. Engagement chart
# --------------------------------

category_summary["avg_engagement"].sort_values().plot(
    kind="barh",
    figsize=(10, 7)
)

plt.xlabel("Average Engagement Score")
plt.ylabel("Category")
plt.title("Average Engagement Score by Category")

plt.tight_layout()

plt.savefig(
    "data/final/category_engagement.png",
    dpi=300
)

plt.show()


# --------------------------------
# 8. Popularity chart
# --------------------------------

category_summary["avg_popularity"].sort_values().plot(
    kind="barh",
    figsize=(10, 7)
)

plt.xlabel("Average Popularity Score")
plt.ylabel("Category")
plt.title("Average Popularity Score by Category")

plt.tight_layout()

plt.savefig(
    "data/final/category_popularity.png",
    dpi=300
)

plt.show()


# --------------------------------
# 9. Rating chart
# --------------------------------

category_summary["avg_rating"].sort_values().plot(
    kind="barh",
    figsize=(10, 7)
)

plt.xlabel("Average Rating")
plt.ylabel("Category")
plt.title("Average Rating by Category")

plt.tight_layout()

plt.savefig(
    "data/final/category_rating.png",
    dpi=300
)

plt.show()
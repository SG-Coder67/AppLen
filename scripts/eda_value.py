import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

# Only apps with comparable positive prices and engagement
value_df = df[
    df["normalized_monthly_price"].notna()
    & (df["normalized_monthly_price"] > 0)
    & df["engagement_score"].notna()
    & df["price_adjusted_value_score"].notna()
].copy()


# --------------------------------
# 1. Price vs Engagement
# --------------------------------

print("\n===== PRICE VS ENGAGEMENT =====")

correlation = value_df[
    ["normalized_monthly_price", "engagement_score"]
].corr().iloc[0, 1]

print(
    f"Correlation between price and engagement: {correlation:.4f}"
)


# --------------------------------
# 2. Value score statistics
# --------------------------------

print("\n===== PRICE-ADJUSTED VALUE =====")

print(
    value_df["price_adjusted_value_score"].describe()
)


# --------------------------------
# 3. Highest value scores
# --------------------------------

print("\n===== TOP 10 PRICE-ADJUSTED VALUE =====")

top_value = (
    value_df[
        [
            "app_name",
            "category",
            "normalized_monthly_price",
            "engagement_score",
            "price_adjusted_value_score"
        ]
    ]
    .sort_values(
        "price_adjusted_value_score",
        ascending=False
    )
    .head(10)
)

print(top_value.to_string(index=False))


# --------------------------------
# 4. Lowest value scores
# --------------------------------

print("\n===== LOWEST 10 PRICE-ADJUSTED VALUE =====")

low_value = (
    value_df[
        [
            "app_name",
            "category",
            "normalized_monthly_price",
            "engagement_score",
            "price_adjusted_value_score"
        ]
    ]
    .sort_values(
        "price_adjusted_value_score",
        ascending=True
    )
    .head(10)
)

print(low_value.to_string(index=False))


# --------------------------------
# 5. Price vs Engagement chart
# --------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    value_df["normalized_monthly_price"],
    value_df["engagement_score"]
)

plt.xlabel("Monthly Price (INR)")
plt.ylabel("Engagement Score")
plt.title("Monthly Price vs Engagement")

plt.tight_layout()

plt.savefig(
    "data/final/price_vs_engagement.png",
    dpi=300
)

plt.show()


# --------------------------------
# 6. Price vs Value chart
# --------------------------------

plt.figure(figsize=(8, 6))

plt.scatter(
    value_df["normalized_monthly_price"],
    value_df["price_adjusted_value_score"]
)

plt.xlabel("Monthly Price (INR)")
plt.ylabel("Price-Adjusted Value Score")
plt.title("Monthly Price vs Price-Adjusted Value")

plt.tight_layout()

plt.savefig(
    "data/final/price_vs_value.png",
    dpi=300
)

plt.show()


# --------------------------------
# 7. Value by category
# --------------------------------

print("\n===== VALUE BY CATEGORY =====")

category_value = (
    value_df
    .groupby("category")["price_adjusted_value_score"]
    .agg(["mean", "median", "count"])
    .sort_values("mean", ascending=False)
)

print(category_value)
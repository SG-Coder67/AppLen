import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

# -----------------------------
# 1. Pricing coverage
# -----------------------------

print("\n===== PRICING COVERAGE =====")

print("Total apps:", len(df))

print(
    "Apps with monthly price:",
    df["normalized_monthly_price"].notna().sum()
)

print(
    "Apps with yearly price:",
    df["normalized_yearly_price"].notna().sum()
)

print(
    "Apps with comparable monthly price:",
    (
        df["normalized_monthly_price"].notna()
        & (df["normalized_monthly_price"] > 0)
    ).sum()
)


# -----------------------------
# 2. Pricing type distribution
# -----------------------------

print("\n===== PRICING TYPE =====")

print(
    df["pricing_type"]
    .value_counts()
)


# -----------------------------
# 3. Price tier distribution
# -----------------------------

print("\n===== PRICE TIER =====")

print(
    df["price_tier"]
    .value_counts()
)


# -----------------------------
# 4. Free / Freemium / Paid
# -----------------------------

print("\n===== FREE TRIAL =====")

print(
    df["has_free_trial"]
    .value_counts()
)


print("\n===== FREEMIUM =====")

print(
    df["is_freemium"]
    .value_counts()
)


# -----------------------------
# 5. Monthly price statistics
# -----------------------------

print("\n===== MONTHLY PRICE STATISTICS =====")

priced_apps = df[
    df["normalized_monthly_price"].notna()
    & (df["normalized_monthly_price"] > 0)
]

print(
    priced_apps["normalized_monthly_price"]
    .describe()
)


# -----------------------------
# 6. Cheapest and most expensive
# -----------------------------

print("\n===== CHEAPEST APPS =====")

cheapest = (
    priced_apps[
        [
            "app_name",
            "category",
            "normalized_monthly_price",
            "pricing_type"
        ]
    ]
    .sort_values("normalized_monthly_price")
    .head(10)
)

print(cheapest.to_string(index=False))


print("\n===== MOST EXPENSIVE APPS =====")

expensive = (
    priced_apps[
        [
            "app_name",
            "category",
            "normalized_monthly_price",
            "pricing_type"
        ]
    ]
    .sort_values(
        "normalized_monthly_price",
        ascending=False
    )
    .head(10)
)

print(expensive.to_string(index=False))


# -----------------------------
# 7. Annual discount
# -----------------------------

print("\n===== ANNUAL DISCOUNT =====")

discounted = df[
    df["annual_discount_pct"].notna()
]

print(
    discounted[
        [
            "app_name",
            "monthly_price",
            "yearly_price",
            "currency",
            "annual_discount_pct"
        ]
    ]
    .sort_values(
        "annual_discount_pct",
        ascending=False
    )
    .to_string(index=False)
)


# -----------------------------
# 8. Average price by category
# -----------------------------

print("\n===== PRICE BY CATEGORY =====")

category_price = (
    priced_apps
    .groupby("category")["normalized_monthly_price"]
    .agg(["mean", "median", "count"])
    .sort_values("mean", ascending=False)
)

print(category_price)


# -----------------------------
# 9. Price tier chart
# -----------------------------

df["price_tier"].value_counts().plot(
    kind="bar",
    figsize=(8, 5)
)

plt.xlabel("Price Tier")
plt.ylabel("Number of Apps")
plt.title("App Distribution by Price Tier")

plt.tight_layout()

plt.savefig(
    "data/final/price_tier_distribution.png",
    dpi=300
)

plt.show()


# -----------------------------
# 10. Monthly price distribution
# -----------------------------

priced_apps["normalized_monthly_price"].plot(
    kind="hist",
    bins=10,
    figsize=(8, 5)
)

plt.xlabel("Monthly Price (INR)")
plt.ylabel("Number of Apps")
plt.title("Distribution of Monthly Subscription Prices")

plt.tight_layout()

plt.savefig(
    "data/final/monthly_price_distribution.png",
    dpi=300
)

plt.show()
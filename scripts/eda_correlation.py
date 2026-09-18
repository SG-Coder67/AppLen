import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "data/final/apps_features.csv"

df = pd.read_csv(INPUT_FILE)

columns = [
    "rating",
    "downloads_numeric",
    "log_downloads",
    "popularity_score",
    "engagement_score",
    "normalized_monthly_price",
    "annual_discount_pct",
    "price_adjusted_value_score"
]

correlation = df[columns].corr()

print("\n===== CORRELATION MATRIX =====")
print(correlation.round(3))


# --------------------------------
# Selected correlations
# --------------------------------

pairs = [
    ("rating", "popularity_score"),
    ("rating", "engagement_score"),
    ("popularity_score", "engagement_score"),
    ("normalized_monthly_price", "engagement_score"),
    ("normalized_monthly_price", "price_adjusted_value_score"),
    ("annual_discount_pct", "engagement_score"),
]

print("\n===== SELECTED CORRELATIONS =====")

for col1, col2 in pairs:
    value = df[[col1, col2]].corr().iloc[0, 1]
    print(f"{col1} vs {col2}: {value:.4f}")


# --------------------------------
# Correlation heatmap
# --------------------------------

plt.figure(figsize=(10, 8))

plt.imshow(
    correlation,
    interpolation="nearest",
    aspect="auto"
)

plt.colorbar()

plt.xticks(
    range(len(columns)),
    columns,
    rotation=45,
    ha="right"
)

plt.yticks(
    range(len(columns)),
    columns
)

plt.title("Correlation Matrix of App Metrics")

plt.tight_layout()

plt.savefig(
    "data/final/correlation_matrix.png",
    dpi=300
)

plt.show()
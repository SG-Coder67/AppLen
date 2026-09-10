import pandas as pd
import numpy as np

INPUT_FILE = "data/final/apps_final.csv"
OUTPUT_FILE = "data/final/apps_features.csv"

# Fixed conversion rate for reproducible analysis
USD_TO_INR = 85


def feature_engineering():

    df = pd.read_csv(INPUT_FILE)

    # --------------------------------------------------
    # 1. Normalize prices to INR
    # --------------------------------------------------

    df["normalized_monthly_price"] = np.where(
        df["currency"].eq("USD"),
        df["monthly_price"] * USD_TO_INR,
        df["monthly_price"]
    )

    df["normalized_yearly_price"] = np.where(
        df["currency"].eq("USD"),
        df["yearly_price"] * USD_TO_INR,
        df["yearly_price"]
    )

    # --------------------------------------------------
    # 2. Annualized cost of monthly subscription
    # --------------------------------------------------

    df["annualized_monthly_cost"] = (
        df["normalized_monthly_price"] * 12
    )

    # --------------------------------------------------
    # 3. Annual savings from yearly plan
    # --------------------------------------------------

    df["annual_savings"] = (
        df["annualized_monthly_cost"]
        - df["normalized_yearly_price"]
    )

    # --------------------------------------------------
    # 4. Annual discount percentage
    # --------------------------------------------------

    df["annual_discount_pct"] = np.where(
        df["annualized_monthly_cost"] > 0,
        (
            df["annual_savings"]
            / df["annualized_monthly_cost"]
        ) * 100,
        np.nan
    )

    df["annual_discount_pct"] = df["annual_discount_pct"].round(2)

    # --------------------------------------------------
    # 5. Convert downloads to numeric
    # --------------------------------------------------

    def parse_downloads(value):

        if pd.isna(value):
            return np.nan

        value = str(value).replace(",", "").replace("+", "")

        try:
            return float(value)
        except ValueError:
            return np.nan

    df["downloads_numeric"] = df["downloads"].apply(parse_downloads)

    # --------------------------------------------------
    # 6. Log-transformed downloads
    # --------------------------------------------------

    df["log_downloads"] = np.log10(
        df["downloads_numeric"]
    )

    # --------------------------------------------------
    # 7. Engagement metrics
    # --------------------------------------------------

    # Normalize popularity between 0 and 100
    if df["log_downloads"].notna().any():

        min_downloads = df["log_downloads"].min()
        max_downloads = df["log_downloads"].max()

        if max_downloads != min_downloads:
            df["popularity_score"] = (
                (df["log_downloads"] - min_downloads)
                / (max_downloads - min_downloads)
            ) * 100
        else:
            df["popularity_score"] = 50

    else:
        df["popularity_score"] = np.nan

    # Rating converted to 0–100 scale
    df["rating_score"] = df["rating"] * 20

    # Engagement score
    df["engagement_score"] = (
        df["rating_score"] * 0.6
        + df["popularity_score"] * 0.4
    )

    df["engagement_score"] = df["engagement_score"].round(2)

    # --------------------------------------------------
    # 8. Price tiers
    # --------------------------------------------------

    def get_price_tier(price):

        if pd.isna(price):
            return "Not Comparable"

        if price == 0:
            return "Free"

        if price < 200:
            return "Low"

        if price < 500:
            return "Medium"

        return "High"

    df["price_tier"] = df[
        "normalized_monthly_price"
    ].apply(get_price_tier)

    # --------------------------------------------------
    # 9. Free trial
    # --------------------------------------------------

    df["has_free_trial"] = (
        df["free_trial_days"].fillna(0) > 0
    )

    # --------------------------------------------------
    # 10. Freemium indicator
    # --------------------------------------------------

    df["is_freemium"] = (
        df["pricing_type"]
        .str.lower()
        .eq("freemium")
    )

    # --------------------------------------------------
    # 11. Verified pricing indicator
    # --------------------------------------------------

    df["is_verified_price"] = (
        df["pricing_status"]
        .str.lower()
        .eq("verified")
    )

    # --------------------------------------------------
    # 12. Price-adjusted value score
    # --------------------------------------------------

    # Only calculate when a comparable paid price exists.
    #
    # Lower price + higher engagement = better value.

    comparable = (
        df["normalized_monthly_price"].notna()
        & (df["normalized_monthly_price"] > 0)
        & df["engagement_score"].notna()
    )

    df["price_adjusted_value_score"] = np.nan

    if comparable.any():

        max_price = df.loc[
            comparable,
            "normalized_monthly_price"
        ].max()

        df.loc[
            comparable,
            "price_adjusted_value_score"
        ] = (
            df.loc[
                comparable,
                "engagement_score"
            ]
            * (
                1 -
                (
                    df.loc[
                        comparable,
                        "normalized_monthly_price"
                    ] / max_price
                )
            )
        )

    df["price_adjusted_value_score"] = (
        df["price_adjusted_value_score"].round(2)
    )

    # --------------------------------------------------
    # 13. Save
    # --------------------------------------------------

    df.to_csv(OUTPUT_FILE, index=False)

    print("Feature engineering completed successfully!")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {OUTPUT_FILE}")

    print("\nNew features:")
    new_features = [
        "normalized_monthly_price",
        "normalized_yearly_price",
        "annualized_monthly_cost",
        "annual_savings",
        "annual_discount_pct",
        "downloads_numeric",
        "log_downloads",
        "popularity_score",
        "rating_score",
        "engagement_score",
        "price_tier",
        "has_free_trial",
        "is_freemium",
        "is_verified_price",
        "price_adjusted_value_score"
    ]

    for feature in new_features:
        print(f"- {feature}")

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicates:", df.duplicated().sum())


if __name__ == "__main__":
    feature_engineering()
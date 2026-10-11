from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apps_metadata_unified.csv"
)

REPORT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apps_metadata_unified_report.txt"
)


def validate_dataset():
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    required_columns = [
        "app_id",
        "app_name",
        "developer",
        "price",
        "currency",
        "is_free_download",
        "rating",
        "rating_count",
        "metadata_source",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    report = []

    def record(message):
        print(message)
        report.append(message)

    record("UNIFIED METADATA VALIDATION")
    record("=" * 40)

    record(f"Total rows: {len(df)}")
    record(f"Unique app IDs: {df['app_id'].nunique()}")
    record(
        f"Duplicate app IDs: {df['app_id'].duplicated().sum()}"
    )
    record(f"Missing app IDs: {df['app_id'].isna().sum()}")

    record("\nMissing values:")
    for column in [
        "app_name",
        "developer",
        "discovery_category",
        "store_category",
        "price",
        "currency",
        "rating",
        "rating_count",
        "description",
    ]:
        if column in df.columns:
            record(
                f"  {column}: {df[column].isna().sum()}"
            )

    price = pd.to_numeric(df["price"], errors="coerce")
    rating = pd.to_numeric(df["rating"], errors="coerce")
    rating_count = pd.to_numeric(
        df["rating_count"], errors="coerce"
    )

    record("\nPricing checks:")
    record(f"Negative prices: {(price < 0).sum()}")
    record(f"Zero prices: {(price == 0).sum()}")
    record(f"Missing/unparseable prices: {price.isna().sum()}")

    record("\nRating checks:")
    record(
        f"Ratings below 0: {(rating < 0).sum()}"
    )
    record(
        f"Ratings above 5: {(rating > 5).sum()}"
    )
    record(
        f"Negative rating counts: {(rating_count < 0).sum()}"
    )

    record("\nSource breakdown:")
    record(
        df["metadata_source"]
        .value_counts(dropna=False)
        .to_string()
    )

    if "is_free_download" in df.columns:
        record("\nDownload pricing classification:")
        record(
            df["is_free_download"]
            .value_counts(dropna=False)
            .to_string()
        )

        free = df["is_free_download"].astype("string").str.lower()
        free_with_price = (
            free.isin(["true", "1"])
            & price.notna()
            & (price > 0)
        )
        paid_without_price = (
            free.isin(["false", "0"])
            & (price.isna() | (price == 0))
        )

        record(
            f"Free downloads with positive prices: "
            f"{free_with_price.sum()}"
        )
        record(
            f"Paid downloads with missing/zero prices: "
            f"{paid_without_price.sum()}"
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"\nReport saved to: {REPORT_PATH}")

    if df["app_id"].isna().any():
        raise ValueError("Missing app IDs detected.")

    if df["app_id"].duplicated().any():
        raise ValueError("Duplicate app IDs detected.")

    print("\nValidation completed. Review the report before proceeding.")


if __name__ == "__main__":
    validate_dataset()
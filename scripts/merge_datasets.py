import pandas as pd


METADATA_FILE = "data/cleaned/apps_cleaned.csv"
PRICING_FILE = "data/raw/apps_pricing.csv"
OUTPUT_FILE = "data/final/apps_final.csv"


def merge_datasets():

    metadata = pd.read_csv(METADATA_FILE)
    pricing = pd.read_csv(PRICING_FILE)

    # Clean app names
    metadata["app_name"] = metadata["app_name"].str.strip()
    pricing["app_name"] = pricing["app_name"].str.strip()

    # Convert pricing date to datetime
    pricing["pricing_date"] = pd.to_datetime(
        pricing["pricing_date"],
        errors="coerce"
    )

    # Sort so the newest pricing record comes first
    pricing = pricing.sort_values(
        "pricing_date",
        ascending=False
    )

    # Keep only the latest record for each app
    pricing = pricing.drop_duplicates(
        subset="app_name",
        keep="first"
    )

    # Merge metadata + pricing
    final_df = metadata.merge(
        pricing,
        on="app_name",
        how="left"
    )

    # Save final dataset
    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Final dataset created successfully!")
    print(f"Rows: {len(final_df)}")
    print(f"Columns: {len(final_df.columns)}")

    print("\nColumns:")
    print(final_df.columns.tolist())

    print("\nMissing values:")
    print(final_df.isnull().sum())

    print("\nDuplicates:", final_df.duplicated().sum())


if __name__ == "__main__":
    merge_datasets()
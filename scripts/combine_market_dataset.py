from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DETAILS_PATH = PROJECT_ROOT / "data" / "raw" / "apps_details.csv"
PAID_PATH = PROJECT_ROOT / "data" / "raw" / "apps_paid_candidates.csv"

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "apps_market_dataset.csv"

PRICE_VERIFICATION_DATE = "2026-10-09"

# These two paid-app prices were manually verified.
VERIFIED_PRICES = {
    "com.sailgrib_wr.paid": 12700,
    "net.osmand.plus": 5000,
}

HIGH_PRICE_THRESHOLD = 5000


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def parse_bool(value):
    """
    Convert Boolean-like values to True/False.
    Preserve missing or unrecognized values as pd.NA.

    Handles:
    True, False, 1, 0, 1.0, 0.0, "true", "false",
    "yes", "no", and missing values.
    """
    if pd.isna(value):
        return pd.NA

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "1.0", "yes", "y"}:
        return True

    if normalized in {"false", "0", "0.0", "no", "n"}:
        return False

    return pd.NA


def classify_pricing(row):
    """
    Classify how an app is monetized.

    Important:
    A free download is not necessarily a completely free app.
    In-app purchases and subscription details may be unavailable.
    """
    free_download = row.get("is_free_download")
    price = row.get("price")
    offers_iap = row.get("offers_in_app_purchases")

    if pd.isna(free_download):
        return "unknown"

    if not bool(free_download):
        if pd.notna(price) and price > 0:
            return "paid_download"

        return "paid_download_price_unknown"

    if pd.isna(offers_iap):
        return "free_download_monetization_unknown"

    if bool(offers_iap):
        return "free_download_with_in_app_purchases"

    return "free_download_no_iap_reported"


# --------------------------------------------------
# Step 1: Check input files
# --------------------------------------------------

print("=" * 60)
print("APPLEN MARKET DATASET BUILDER")
print("=" * 60)

for path in [DETAILS_PATH, PAID_PATH]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required input file not found: {path}"
        )

print("\nInput files found.")


# --------------------------------------------------
# Step 2: Load datasets
# --------------------------------------------------

details = pd.read_csv(DETAILS_PATH)
paid = pd.read_csv(PAID_PATH)

print(f"\nFree-download app records: {len(details)}")
print(f"Paid-app candidate records: {len(paid)}")

# Only require columns essential for identifying apps and their prices.
required_columns = {
    "app_id",
    "is_free_download",
    "price",
}

for dataset_name, dataset in [
    ("apps_details.csv", details),
    ("apps_paid_candidates.csv", paid),
]:
    missing_columns = required_columns - set(dataset.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )

# The paid-app dataset may not provide these fields.
# Add missing columns without inventing values.
for column in [
    "offers_in_app_purchases",
    "contains_ads",
]:
    if column not in details.columns:
        details[column] = pd.NA

    if column not in paid.columns:
        paid[column] = pd.NA

# --------------------------------------------------
# Step 3: Identify dataset sources
# --------------------------------------------------

details = details.copy()
paid = paid.copy()

details["source_dataset"] = "apps_details"
paid["source_dataset"] = "apps_paid_candidates"


# --------------------------------------------------
# Step 4: Combine datasets
# --------------------------------------------------

# Paid candidates come first so their pricing information
# takes priority when duplicate app IDs are encountered.
combined = pd.concat(
    [paid, details],
    ignore_index=True,
    sort=False,
)

print(f"\nCombined records before cleaning: {len(combined)}")


# --------------------------------------------------
# Step 5: Clean app IDs
# --------------------------------------------------

combined["app_id"] = combined["app_id"].astype("string").str.strip()

combined = combined[
    combined["app_id"].notna()
    & combined["app_id"].ne("")
].copy()


# --------------------------------------------------
# Step 6: Convert numeric columns
# --------------------------------------------------

numeric_columns = [
    "price",
    "rating",
    "rating_count",
    "downloads",
    "in_app_product_price",
]

for column in numeric_columns:
    if column in combined.columns:
        combined[column] = pd.to_numeric(
            combined[column],
            errors="coerce",
        )


# --------------------------------------------------
# Step 7: Normalize Boolean columns
# --------------------------------------------------

# FIX:
# pd.concat may convert True/False into 1.0/0.0 when
# one dataset contains missing values.
#
# This parser correctly handles both representations.
# Missing values remain missing instead of becoming False.

boolean_columns = [
    "is_free_download",
    "offers_in_app_purchases",
    "contains_ads",
]

for column in boolean_columns:
    if column in combined.columns:
        combined[column] = pd.array(
            combined[column].map(parse_bool),
            dtype="boolean",
        )


# --------------------------------------------------
# Step 8: Deduplicate by app ID
# --------------------------------------------------

# The paid dataset is listed first. GroupBy.first()
# takes the first non-null value for each column.
combined = (
    combined.groupby(
        "app_id",
        as_index=False,
        sort=False,
    )
    .first()
)

print(f"Unique apps after deduplication: {len(combined)}")


# --------------------------------------------------
# Step 9: Classify pricing models
# --------------------------------------------------

combined["pricing_model"] = combined.apply(
    classify_pricing,
    axis=1,
)


# --------------------------------------------------
# Step 10: Track manually verified prices
# --------------------------------------------------

combined["price_manually_verified"] = False
combined["price_verification_date"] = pd.NA

for app_id, verified_price in VERIFIED_PRICES.items():
    mask = combined["app_id"].eq(app_id)

    if mask.any():
        actual_price = combined.loc[mask, "price"].iloc[0]

        if pd.notna(actual_price) and actual_price == verified_price:
            combined.loc[
                mask, "price_manually_verified"
            ] = True

            combined.loc[
                mask, "price_verification_date"
            ] = PRICE_VERIFICATION_DATE
        else:
            print(
                f"WARNING: Verified price mismatch for {app_id}. "
                f"Expected ₹{verified_price}; found {actual_price}."
            )


# --------------------------------------------------
# Step 11: Flag expensive apps for review
# --------------------------------------------------

combined["high_price_flag"] = (
    combined["price"].notna()
    & (combined["price"] >= HIGH_PRICE_THRESHOLD)
)


# --------------------------------------------------
# Step 12: Sort and save
# --------------------------------------------------

combined = combined.sort_values(
    by=["pricing_model", "app_id"],
    ascending=[True, True],
).reset_index(drop=True)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

combined.to_csv(
    OUTPUT_PATH,
    index=False,
)


# --------------------------------------------------
# Step 13: Validate the dataset
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATASET VALIDATION")
print("=" * 60)

print(f"\nTotal unique apps: {len(combined)}")
print(f"Duplicate app IDs: {combined['app_id'].duplicated().sum()}")
print(f"Missing app IDs: {combined['app_id'].isna().sum()}")
print(f"Missing prices: {combined['price'].isna().sum()}")
print(
    f"Negative prices: "
    f"{(combined['price'].dropna() < 0).sum()}"
)
print(
    f"Manually verified prices: "
    f"{combined['price_manually_verified'].sum()}"
)
print(
    f"Apps priced at ₹{HIGH_PRICE_THRESHOLD:,} or above: "
    f"{combined['high_price_flag'].sum()}"
)

print("\nPricing models:")
print(combined["pricing_model"].value_counts(dropna=False).to_string())

print("\nIn-app purchase values:")
print(
    combined["offers_in_app_purchases"]
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# Step 14: Sanity checks
# --------------------------------------------------

assert combined["app_id"].isna().sum() == 0, (
    "Validation failed: missing app IDs."
)

assert combined["app_id"].duplicated().sum() == 0, (
    "Validation failed: duplicate app IDs."
)

assert not (combined["price"].dropna() < 0).any(), (
    "Validation failed: negative prices found."
)

# These counts are expected from the current input files.
# They help catch accidental Boolean-conversion regressions.
expected_pricing_counts = {
    "free_download_with_in_app_purchases": 167,
    "free_download_no_iap_reported": 186,
    "paid_download": 31,
}

for pricing_model, expected_count in expected_pricing_counts.items():
    actual_count = int(
        (combined["pricing_model"] == pricing_model).sum()
    )

    assert actual_count == expected_count, (
        f"Unexpected count for '{pricing_model}': "
        f"expected {expected_count}, got {actual_count}. "
        "Check the input datasets before using the output."
    )

assert int(combined["offers_in_app_purchases"].eq(True).sum()) == 167, (
    "Expected 167 apps with in-app purchases."
)

assert int(combined["offers_in_app_purchases"].eq(False).sum()) == 186, (
    "Expected 186 apps without reported in-app purchases."
)

assert int(combined["offers_in_app_purchases"].isna().sum()) == 31, (
    "Expected 31 missing in-app purchase values."
)

print("\nAll validation checks passed.")
print(f"Output saved to:\n{OUTPUT_PATH}")
print(f"\nFinal dataset shape: {combined.shape}")
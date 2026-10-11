from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "apps_details.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "apps_metadata_validated.csv"
REPORT_PATH = OUTPUT_DIR / "apps_metadata_validation_report.txt"


# --------------------------------------------------
# Validation
# --------------------------------------------------

def validate_metadata():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Metadata input file not found: {INPUT_PATH}"
        )

    df = pd.read_csv(INPUT_PATH)

    original_rows = len(df)
    original_columns = len(df.columns)

    print("=" * 60)
    print("APPLEN METADATA VALIDATION")
    print("=" * 60)

    print(f"\nInput file: {INPUT_PATH}")
    print(f"Original rows: {original_rows}")
    print(f"Original columns: {original_columns}")

    # --------------------------------------------------
    # 1. Validate required columns
    # --------------------------------------------------

    required_columns = [
        "app_id",
        "app_name",
        "rating",
        "price",
        "min_installs",
        "real_installs",
        "is_free_download",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    # --------------------------------------------------
    # 2. Normalize app IDs
    # --------------------------------------------------

    df["app_id"] = df["app_id"].astype("string").str.strip()

    missing_id_mask = (
        df["app_id"].isna()
        | df["app_id"].eq("")
    )

    missing_id_count = int(missing_id_mask.sum())

    # Remove records only when their app ID is missing.
    df = df.loc[~missing_id_mask].copy()

    # Count duplicate IDs before removing duplicates.
    duplicate_id_mask = df["app_id"].duplicated(keep="first")
    duplicate_id_count = int(duplicate_id_mask.sum())

    df = df.loc[~duplicate_id_mask].copy()

    # --------------------------------------------------
    # 3. Normalize numeric columns
    # --------------------------------------------------

    numeric_columns = [
        "rating",
        "rating_count",
        "min_installs",
        "real_installs",
        "price",
    ]

    for column in numeric_columns:
        if column in df.columns:
            original_non_missing = df[column].notna()

            converted = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            # Count non-empty values that could not be parsed.
            invalid_mask = original_non_missing & converted.isna()

            df[f"{column}_invalid_format"] = invalid_mask

            df[column] = converted

    # --------------------------------------------------
    # 4. Validate numeric ranges
    # --------------------------------------------------

    invalid_rating_mask = (
        df["rating"].notna()
        & ~df["rating"].between(0, 5)
    )

    negative_price_mask = (
        df["price"].notna()
        & (df["price"] < 0)
    )

    invalid_install_masks = {}

    for column in ["min_installs", "real_installs"]:
        if column in df.columns:
            invalid_install_masks[column] = (
                df[column].notna()
                & (df[column] < 0)
            )

    # Flag suspicious free-download records with positive prices.
    free_download = (
        df["is_free_download"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    positive_price_on_free_download_mask = (
        free_download.isin(["true", "1", "1.0", "yes", "y"])
        & df["price"].notna()
        & (df["price"] > 0)
    )

    # Flag paid-download records with zero or missing prices.
    paid_download_mask = free_download.isin(
        ["false", "0", "0.0", "no", "n"]
    )

    paid_price_missing_or_zero_mask = (
        paid_download_mask
        & (
            df["price"].isna()
            | df["price"].eq(0)
        )
    )

    # --------------------------------------------------
    # 5. Check metadata completeness
    # --------------------------------------------------

    completeness_columns = [
        column
        for column in [
            "app_name",
            "store_category",
            "developer",
            "rating",
            "rating_count",
            "price",
            "description",
            "released",
            "last_updated",
        ]
        if column in df.columns
    ]

    missing_values = df[completeness_columns].isna().sum()

    # --------------------------------------------------
    # 6. Build validation report
    # --------------------------------------------------

    invalid_numeric_counts = {
        column: int(df[f"{column}_invalid_format"].sum())
        for column in numeric_columns
        if f"{column}_invalid_format" in df.columns
    }

    invalid_install_counts = {
        column: int(mask.sum())
        for column, mask in invalid_install_masks.items()
    }

    report_lines = [
        "APPLEN METADATA VALIDATION REPORT",
        "=" * 40,
        f"Input file: {INPUT_PATH}",
        f"Output file: {OUTPUT_PATH}",
        f"Original rows: {original_rows}",
        f"Original columns: {original_columns}",
        f"Rows with missing app IDs removed: {missing_id_count}",
        f"Duplicate app ID rows removed: {duplicate_id_count}",
        f"Validated rows: {len(df)}",
        f"Validated columns: {len(df.columns)}",
        "",
        "NUMERIC FORMAT ISSUES",
        "-" * 40,
    ]

    for column, count in invalid_numeric_counts.items():
        report_lines.append(f"{column}: {count}")

    report_lines.extend([
        "",
        "RANGE AND PRICING CHECKS",
        "-" * 40,
        f"Ratings outside 0-5: {int(invalid_rating_mask.sum())}",
        f"Negative prices: {int(negative_price_mask.sum())}",
        f"Negative installation counts: {invalid_install_counts}",
        (
            "Free downloads with positive listed prices: "
            f"{int(positive_price_on_free_download_mask.sum())}"
        ),
        (
            "Paid downloads with zero or missing prices: "
            f"{int(paid_price_missing_or_zero_mask.sum())}"
        ),
        "",
        "MISSING METADATA VALUES",
        "-" * 40,
    ])

    for column, count in missing_values.items():
        report_lines.append(f"{column}: {int(count)}")

    report_lines.extend([
        "",
        "IMPORTANT",
        "-" * 40,
        "Missing ratings, prices, dates, and descriptions were not invented.",
        "Pricing inconsistencies are flagged for review, not automatically changed.",
        "The raw input dataset was not modified.",
    ])

    # --------------------------------------------------
    # 7. Save validated dataset and report
    # --------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    REPORT_PATH.write_text(
        "\n".join(report_lines),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # 8. Display results
    # --------------------------------------------------

    print("\n--- Validation summary ---")
    print(f"Original rows: {original_rows}")
    print(f"Rows with missing app IDs removed: {missing_id_count}")
    print(f"Duplicate app ID rows removed: {duplicate_id_count}")
    print(f"Validated rows: {len(df)}")

    print("\n--- Numeric format issues ---")
    for column, count in invalid_numeric_counts.items():
        print(f"{column}: {count}")

    print("\n--- Range and pricing checks ---")
    print(
        "Ratings outside 0-5:",
        int(invalid_rating_mask.sum()),
    )
    print(
        "Negative prices:",
        int(negative_price_mask.sum()),
    )
    print(
        "Negative installation counts:",
        invalid_install_counts,
    )
    print(
        "Free downloads with positive listed prices:",
        int(positive_price_on_free_download_mask.sum()),
    )
    print(
        "Paid downloads with zero or missing prices:",
        int(paid_price_missing_or_zero_mask.sum()),
    )

    print("\n--- Missing metadata ---")
    print(missing_values.to_string())

    print("\nValidation completed.")
    print(f"Validated dataset: {OUTPUT_PATH}")
    print(f"Validation report: {REPORT_PATH}")


if __name__ == "__main__":
    validate_metadata()
from pathlib import Path

import pandas as pd


# Resolve paths relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

METADATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apps_metadata_validated.csv"
)

PAID_CANDIDATES_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "apps_paid_candidates.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "apps_metadata_unified.csv"
)


def build_unified_metadata():
    # 1. Load the source datasets.
    metadata = pd.read_csv(METADATA_PATH, low_memory=False)
    paid_candidates = pd.read_csv(
        PAID_CANDIDATES_PATH,
        low_memory=False,
    )

    # 2. Normalize app IDs.
    metadata["app_id"] = (
        metadata["app_id"].astype("string").str.strip()
    )
    paid_candidates["app_id"] = (
        paid_candidates["app_id"].astype("string").str.strip()
    )

    metadata = metadata.dropna(subset=["app_id"]).copy()
    paid_candidates = paid_candidates.dropna(
        subset=["app_id"]
    ).copy()

    # 3. Validate source datasets before merging.
    if metadata["app_id"].duplicated().any():
        raise ValueError(
            "Duplicate app IDs found in validated metadata."
        )

    if paid_candidates["app_id"].duplicated().any():
        raise ValueError(
            "Duplicate app IDs found in paid candidates."
        )

    # 4. Find paid candidates absent from existing metadata.
    existing_ids = set(metadata["app_id"])

    additional_apps = paid_candidates[
        ~paid_candidates["app_id"].isin(existing_ids)
    ].copy()

    # 5. Preserve all existing metadata columns and add
    # any additional columns present in paid candidates.
    columns = list(
        dict.fromkeys(
            list(metadata.columns)
            + list(paid_candidates.columns)
            + ["metadata_source"]
        )
    )

    metadata["metadata_source"] = "validated_metadata"

    # Create new rows using the paid-candidate records.
    additional_rows = pd.DataFrame(
        pd.NA,
        index=additional_apps.index,
        columns=columns,
    )

    # Map fields explicitly to avoid accidental column mismatches.
    field_mappings = {
        "app_id": "app_id",
        "app_name": "app_name",
        "discovery_category": "discovery_category",
        "store_category": "store_category",
        "developer": "developer",
        "price": "price",
        "currency": "currency",
        "is_free_download": "is_free_download",
        "rating": "rating",
        "rating_count": "rating_count",
        "installs": "installs",
        "description": "description",
        "app_url": "app_url",
        "country": "country",
    }

    for target, source in field_mappings.items():
        if (
            target in additional_rows.columns
            and source in additional_apps.columns
        ):
            additional_rows[target] = (
                additional_apps[source].to_numpy()
            )

    additional_rows["metadata_source"] = "paid_candidate"

    # 6. Combine existing metadata with new paid candidates.
    unified = pd.concat(
        [
            metadata.reindex(columns=columns),
            additional_rows,
        ],
        ignore_index=True,
    )

    # 7. Final integrity checks.
    if unified["app_id"].duplicated().any():
        raise ValueError(
            "Duplicate app IDs detected. Output was not saved."
        )

    if unified["app_id"].isna().any():
        raise ValueError(
            "Missing app IDs detected. Output was not saved."
        )

    # 8. Save the new dataset without modifying source files.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    unified.to_csv(OUTPUT_PATH, index=False)

    # 9. Print a summary.
    print("\nUNIFIED METADATA DATASET CREATED")
    print("-" * 40)
    print(f"Original metadata apps: {len(metadata)}")
    print(f"Additional paid apps:   {len(additional_rows)}")
    print(f"Total apps:             {len(unified)}")
    print(f"Unique app IDs:         {unified['app_id'].nunique()}")
    print(
        f"Duplicate IDs:          "
        f"{unified['app_id'].duplicated().sum()}"
    )

    print("\nMetadata sources:")
    print(unified["metadata_source"].value_counts().to_string())

    print(f"\nOutput file: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_unified_metadata()
import pandas as pd


def load_master_dataset():
    return pd.read_csv("data/raw/apps_master.csv")


def enrich_dataset(df):
    df["developer"] = None
    df["country_origin"] = None
    df["platform"] = None
    df["rating"] = None
    df["downloads"] = None
    df["monthly_price"] = None
    df["yearly_price"] = None
    df["free_trial_days"] = None
    df["premium_features"] = None

    return df


def save_dataset(df):
    output_path = "data/raw/apps_metadata.csv"

    df.to_csv(output_path, index=False)

    print(f"\nDataset saved successfully!")
    print(f"Location: {output_path}")


def main():
    df = load_master_dataset()

    df = enrich_dataset(df)

    save_dataset(df)


if __name__ == "__main__":
    main()
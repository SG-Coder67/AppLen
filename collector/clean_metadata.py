import pandas as pd


def clean_downloads(value):

    if pd.isna(value):
        return None

    value = value.replace(",", "")
    value = value.replace("+", "")

    return int(value)


def clean_dataset():

    df = pd.read_csv("data/raw/apps_metadata.csv")

    df["downloads"] = df["downloads"].apply(clean_downloads)

    df.to_csv(
        "data/cleaned/apps_cleaned.csv",
        index=False
    )

    print("Dataset cleaned successfully!")


if __name__ == "__main__":
    clean_dataset()
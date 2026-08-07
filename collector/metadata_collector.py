import pandas as pd
from google_play_scraper import search


def get_app(app_name):

    results = search(
        app_name,
        lang="en",
        country="in",
        n_hits=1
    )

    if not results:
        return None

    return results[0]


def enrich_metadata():

    df = pd.read_csv("data/raw/apps_master.csv")

    developers = []
    ratings = []
    downloads = []
    failed_apps = []
    for app_name in df["app_name"]:
    
        print(f"Fetching {app_name}...")
        try:
            app = get_app(app_name)
            if app:
                developers.append(app.get("developer"))
                ratings.append(app.get("score"))
                downloads.append(app.get("installs"))
            else:
                developers.append(None)
                ratings.append(None)
                downloads.append(None)
        except Exception as e:
            print(f"Error fetching {app_name}: {e}")
            developers.append(None)
            ratings.append(None)
            downloads.append(None)
            failed_apps.append(app_name)

    df["developer"] = developers
    df["rating"] = ratings
    df["downloads"] = downloads
    print("\nFailed Apps:")
    for app in failed_apps:
        print(app)
    df.to_csv(
        "data/raw/apps_metadata.csv",
        index=False
    )

    print("\nMetadata collection completed!")


if __name__ == "__main__":
    enrich_metadata()
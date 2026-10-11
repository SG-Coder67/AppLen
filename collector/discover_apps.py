import json
import time
from pathlib import Path

import pandas as pd
from google_play_scraper import search


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "apps_discovered.csv"
FAILED_QUERIES_PATH = PROJECT_ROOT / "data" / "raw" / "apps_discovery_failures.csv"
PROGRESS_PATH = (
    PROJECT_ROOT / "data" / "raw" / "apps_discovery_progress.json"
)
COUNTRY = "in"
LANGUAGE = "en"

# Google Play search result limit per query.
RESULTS_PER_QUERY = 30

# Delay between requests.
REQUEST_DELAY_SECONDS = 1.5

# Target is a milestone, not a guarantee per run.
TARGET_APPS = 5000

# Flush progress to disk after every query.
SAVE_AFTER_EACH_QUERY = True


# --------------------------------------------------
# Discovery queries
# --------------------------------------------------

CATEGORIES = {
    "Finance": [
        "finance",
        "personal finance",
        "expense tracker",
        "budget planner",
        "investment tracker",
        "stock market",
        "mutual funds",
        "tax calculator",
        "loan calculator",
        "digital payments",
        "banking",
        "insurance",
        "cryptocurrency",
    ],
    "Education": [
        "education",
        "online learning",
        "learning apps",
        "online courses",
        "exam preparation",
        "competitive exams",
        "language learning",
        "math learning",
        "coding education",
        "school learning",
        "college learning",
        "educational games",
    ],
    "Shopping": [
        "shopping",
        "fashion shopping",
        "grocery shopping",
        "online marketplace",
        "electronics shopping",
        "beauty shopping",
        "clothing store",
        "deals and discounts",
        "second hand marketplace",
        "price comparison",
    ],
    "Health & Fitness": [
        "health fitness",
        "workout",
        "home workout",
        "meditation",
        "yoga",
        "calorie counter",
        "nutrition tracker",
        "running tracker",
        "sleep tracker",
        "mental wellness",
        "fitness coaching",
        "habit tracker",
    ],
    "Food & Drink": [
        "food delivery",
        "food ordering",
        "restaurant finder",
        "recipe apps",
        "cooking",
        "meal planning",
        "nutrition",
        "grocery delivery",
        "coffee",
        "food discovery",
    ],
    "Productivity": [
        "productivity",
        "notes",
        "task manager",
        "to do list",
        "calendar",
        "document scanner",
        "pdf editor",
        "time tracking",
        "project management",
        "cloud storage",
        "voice notes",
        "password manager",
        "AI assistant",
        "automation",
    ],
    "Travel": [
        "travel",
        "hotel booking",
        "flight booking",
        "train booking",
        "bus booking",
        "travel planning",
        "navigation",
        "offline maps",
        "car rental",
        "trip planner",
        "local transport",
        "travel guide",
    ],
    "Entertainment": [
        "music streaming",
        "video streaming",
        "movie discovery",
        "podcasts",
        "audiobooks",
        "live television",
        "entertainment",
        "comics",
        "short videos",
        "animation",
    ],
    "Communication": [
        "messaging",
        "video calling",
        "email",
        "voice calling",
        "team communication",
        "secure messaging",
        "conference calling",
        "community chat",
    ],
    "Business": [
        "business",
        "accounting",
        "invoicing",
        "business management",
        "point of sale",
        "inventory management",
        "customer relationship management",
        "employee management",
        "business analytics",
        "small business",
        "appointment booking",
        "business finance",
    ],
    "Lifestyle": [
        "lifestyle",
        "personal development",
        "journaling",
        "home organization",
        "interior design",
        "relationship advice",
        "event planning",
        "daily routine",
        "personal assistant",
    ],
    "Tools": [
        "utility tools",
        "file manager",
        "calculator",
        "keyboard",
        "QR scanner",
        "device security",
        "backup tools",
        "screen recorder",
        "file sharing",
        "translation",
        "unit converter",
    ],
    "Photography": [
        "photo editor",
        "camera",
        "video editor",
        "collage maker",
        "photo filters",
        "AI photo editor",
        "background remover",
        "photo management",
        "professional camera",
    ],
    "Medical": [
        "medical",
        "medicine reminder",
        "health records",
        "doctor consultation",
        "pharmacy",
        "medical reference",
        "symptom tracker",
        "hospital management",
        "first aid",
    ],
    "Sports": [
        "sports",
        "sports scores",
        "cricket",
        "football",
        "sports training",
        "running",
        "cycling",
        "sports news",
        "fantasy sports",
    ],
    "News & Magazines": [
        "news",
        "news reader",
        "newspapers",
        "business news",
        "technology news",
        "local news",
        "magazines",
        "news aggregator",
    ],
    "Social": [
        "social networking",
        "community",
        "professional networking",
        "creator community",
        "interest groups",
        "social discovery",
        "forum",
    ],
    "Personalization": [
        "wallpaper",
        "launcher",
        "themes",
        "icons",
        "widgets",
        "customization",
        "live wallpaper",
        "font customization",
    ],
    "Maps & Navigation": [
        "maps navigation",
        "GPS navigation",
        "traffic navigation",
        "offline navigation",
        "route planner",
        "public transport maps",
        "location sharing",
    ],
    "Books & Reference": [
        "ebooks",
        "book reader",
        "dictionary",
        "reference",
        "religious books",
        "novels",
        "study reference",
        "encyclopedia",
    ],
    "Parenting": [
        "parenting",
        "baby tracker",
        "pregnancy tracker",
        "child development",
        "family organizer",
    ],
    "Weather": [
        "weather forecast",
        "weather radar",
        "rain forecast",
        "air quality",
        "weather alerts",
    ],
    "Events": [
        "event booking",
        "event discovery",
        "concert tickets",
        "local events",
        "event management",
    ],
    "Art & Design": [
        "graphic design",
        "drawing",
        "digital art",
        "logo maker",
        "illustration",
        "design tools",
    ],
    "Auto & Vehicles": [
        "car maintenance",
        "vehicle tracking",
        "car marketplace",
        "vehicle information",
        "driving test",
        "automotive",
    ],
}


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def load_existing_results():
    """Load existing discoveries to support resuming."""

    if not OUTPUT_PATH.exists():
        return pd.DataFrame(
            columns=[
                "app_id",
                "app_name",
                "category",
                "search_query",
                "developer",
                "country",
                "language",
            ]
        )

    df = pd.read_csv(OUTPUT_PATH)

    if "app_id" not in df.columns:
        raise ValueError(
            f"{OUTPUT_PATH} does not contain an app_id column."
        )

    df["app_id"] = df["app_id"].astype("string").str.strip()

    df = df[
        df["app_id"].notna()
        & df["app_id"].ne("")
    ].copy()

    # If an older version of this collector created the file,
    # add the newer fields without deleting existing data.
    defaults = {
        "app_name": pd.NA,
        "category": "Unknown",
        "search_query": pd.NA,
        "developer": pd.NA,
        "country": COUNTRY,
        "language": LANGUAGE,
    }

    for column, default_value in defaults.items():
        if column not in df.columns:
            df[column] = default_value

    return df


def load_failed_queries():
    """Load previous failed queries."""

    if not FAILED_QUERIES_PATH.exists():
        return pd.DataFrame(
            columns=["category", "search_query", "error"]
        )

    return pd.read_csv(FAILED_QUERIES_PATH)


def save_results(df):
    """Persist discoveries without overwriting other datasets."""

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = df.drop_duplicates(
        subset=["app_id"],
        keep="first",
    )

    df.to_csv(
        OUTPUT_PATH,
        index=False,
    )


def save_failures(failures):
    """Save failed queries for later inspection."""

    FAILED_QUERIES_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    failures.to_csv(
        FAILED_QUERIES_PATH,
        index=False,
    )


# --------------------------------------------------
# Discovery
# --------------------------------------------------

def discover_apps():
    existing = load_existing_results()
    failures = load_failed_queries()

    # Ensure failures have the expected columns.
    for column in ["category", "search_query", "error"]:
        if column not in failures.columns:
            failures[column] = pd.NA

    # Normalize existing app IDs.
    existing["app_id"] = (
        existing["app_id"]
        .astype("string")
        .str.strip()
    )

    seen_ids = set(existing["app_id"].dropna().tolist())

    print("=" * 65)
    print("APPLEN APP DISCOVERY")
    print("=" * 65)
    print(f"Country: {COUNTRY}")
    print(f"Categories: {len(CATEGORIES)}")
    print(f"Unique apps already saved: {len(seen_ids)}")
    print(f"Target: {TARGET_APPS} unique apps")
    print(f"Output: {OUTPUT_PATH}")

    # Skip queries that have already succeeded in previous runs.
    # Failed queries are retried.
    # Track completed searches separately from discovered app records.
# Existing CSV records alone do not prove that a query is complete.
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH, "r", encoding="utf-8") as file:
            successful_queries = set(json.load(file))
    else:
        successful_queries = set()

    total_queries = sum(
        len(queries)
        for queries in CATEGORIES.values()
    )

    completed_queries = 0

    for category, queries in CATEGORIES.items():
        print(f"\n--- Category: {category} ---")

        for query in queries:
            completed_queries += 1

            if len(seen_ids) >= TARGET_APPS:
                print(
                    f"\nTarget reached: {TARGET_APPS} unique apps."
                )
                save_results(existing)
                save_failures(failures)
                print(f"Saved {len(seen_ids)} unique apps.")
                return

            if query in successful_queries:
                print(
                    f"Skipping completed query: '{query}'"
                )
                continue

            print(
                f"\n[{completed_queries}/{total_queries}] "
                f"Searching: '{query}'"
            )

            try:
                results = search(
                    query,
                    lang=LANGUAGE,
                    country=COUNTRY,
                    n_hits=RESULTS_PER_QUERY,
                )

                new_records = []

                for app in results:
                    app_id = app.get("appId")

                    if not app_id:
                        continue

                    app_id = str(app_id).strip()

                    if not app_id or app_id in seen_ids:
                        continue

                    seen_ids.add(app_id)

                    new_records.append({
                        "app_id": app_id,
                        "app_name": app.get("title"),
                        "category": category,
                        "search_query": query,
                        "developer": app.get("developer"),
                        "country": COUNTRY,
                        "language": LANGUAGE,
                    })

                if new_records:
                    existing = pd.concat(
                        [
                            existing,
                            pd.DataFrame(new_records),
                        ],
                        ignore_index=True,
                        sort=False,
                    )

                print(f"Results returned: {len(results)}")
                print(f"New unique apps: {len(new_records)}")
                print(f"Total unique apps: {len(seen_ids)}")

                # Mark successful queries so a later run can resume.
                successful_queries.add(query)
                with open(PROGRESS_PATH, "w", encoding="utf-8") as file:
                    json.dump(sorted(successful_queries), file, indent=2)
                # Remove stale failure entries for successful queries.
                failures = failures[
                    ~(
                        failures["search_query"]
                        .astype("string")
                        .eq(query)
                    )
                ].copy()

                if SAVE_AFTER_EACH_QUERY:
                    save_results(existing)
                    save_failures(failures)

                time.sleep(REQUEST_DELAY_SECONDS)

            except Exception as error:
                print(f"Query failed: {error}")

                failures = failures[
                    ~(
                        failures["search_query"]
                        .astype("string")
                        .eq(query)
                    )
                ].copy()

                failure_row = pd.DataFrame([{
                    "category": category,
                    "search_query": query,
                    "error": str(error),
                }])

                failures = pd.concat(
                    [failures, failure_row],
                    ignore_index=True,
                )

                save_failures(failures)

                # Continue with the remaining queries.
                time.sleep(REQUEST_DELAY_SECONDS)

    save_results(existing)
    save_failures(failures)

    print("\n" + "=" * 65)
    print("DISCOVERY SUMMARY")
    print("=" * 65)
    print(f"Unique apps discovered: {len(existing)}")
    print(f"Target: {TARGET_APPS}")
    print(f"Remaining: {max(TARGET_APPS - len(existing), 0)}")
    print(f"Failed queries recorded: {len(failures)}")
    print(f"Saved dataset: {OUTPUT_PATH}")
    print(f"Saved failures: {FAILED_QUERIES_PATH}")

    if len(existing) < TARGET_APPS:
        print(
            "\nThe target was not reached in this run. "
            "We can expand the query set and continue discovery."
        )


if __name__ == "__main__":
    discover_apps()
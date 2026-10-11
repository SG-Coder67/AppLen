import time
from pathlib import Path

import pandas as pd
from google_play_scraper import search, app


OUTPUT_PATH = Path("data/raw/apps_paid_candidates.csv")
EXISTING_PATH = Path("data/raw/apps_details.csv")

CATEGORIES = {'Finance': ['paid finance apps', 'premium expense tracker', 'paid investment tools', 'premium tax calculator'], 'Education': ['paid learning apps', 'premium educational apps', 'paid exam preparation', 'premium language learning'], 'Shopping': ['paid shopping apps', 'premium price comparison tools', 'shopping list pro'], 'Health & Fitness': ['premium fitness apps', 'paid workout planner', 'premium meditation', 'paid calorie tracker'], 'Food & Drink': ['premium recipe apps', 'paid meal planner', 'professional cooking tools'], 'Productivity': ['paid productivity apps', 'premium calendar', 'professional document editor', 'notes pro'], 'Travel': ['premium travel tools', 'paid navigation apps', 'offline maps'], 'Entertainment': ['paid entertainment apps', 'premium audiobook player', 'paid video player'], 'Communication': ['paid communication apps', 'premium email client', 'professional calling tools'], 'Business': ['paid business apps', 'professional invoicing', 'business management tools'], 'Lifestyle': ['paid lifestyle apps', 'premium journal', 'personal organizer pro'], 'Tools': ['paid utility tools', 'premium calculator', 'file manager pro', 'QR scanner pro'], 'Photography': ['paid photo editor', 'professional camera', 'premium photo editing'], 'Medical': ['paid medical reference apps', 'premium medicine reminder', 'medical calculator pro'], 'Sports': ['paid sports apps', 'premium sports training', 'professional running tracker'], 'News & Magazines': ['paid news apps', 'premium news reader', 'magazine subscription apps'], 'Social': ['paid social networking apps', 'premium community apps'], 'Personalization': ['paid launcher apps', 'premium icon packs', 'paid live wallpapers', 'themes pro'], 'Maps & Navigation': ['paid GPS navigation', 'premium offline maps', 'paid route planner'], 'Books & Reference': ['paid ebook reader', 'premium dictionary', 'paid reference apps'], 'Parenting': ['premium baby tracker', 'paid parenting apps', 'family organizer pro'], 'Weather': ['paid weather apps', 'premium weather radar', 'professional weather forecast'], 'Events': ['paid event management apps', 'premium event planner', 'event organizer pro'], 'Art & Design': ['paid drawing apps', 'professional graphic design', 'premium digital art tools'], 'Auto & Vehicles': ['paid car maintenance apps', 'premium vehicle tools', 'professional driving apps']}



def discover_paid_candidates():
    existing = pd.read_csv(EXISTING_PATH)
    existing_ids = set(existing["app_id"].dropna().astype(str))

    if OUTPUT_PATH.exists():
        previous = pd.read_csv(OUTPUT_PATH)
        records = previous.to_dict("records")
        seen_ids = set(previous["app_id"].dropna().astype(str))
    else:
        records = []
        seen_ids = set()

    print(f"Existing AppLen apps: {len(existing_ids)}")
    print(f"Previously discovered candidates: {len(seen_ids)}")

    for category, queries in CATEGORIES.items():
        print(f"\nSearching category: {category}")

        for query in queries:
            try:
                results = search(
                    query,
                    lang="en",
                    country="in",
                    n_hits=30,
                )

                print(f"  Query: {query} | Results: {len(results)}")

                for result in results:
                    app_id = result.get("appId")

                    if not app_id:
                        continue

                    app_id = str(app_id)

                    if app_id in existing_ids or app_id in seen_ids:
                        continue

                    try:
                        details = app(
                            app_id,
                            lang="en",
                            country="in",
                        )

                        price = details.get("price")
                        is_free = details.get("free")

                        # Retain only verified paid-download apps.
                        if price is None or is_free is not False or price <= 0:
                            continue

                        records.append({
                            "app_id": app_id,
                            "app_name": details.get("title"),
                            "discovery_category": category,
                            "store_category": details.get("genre"),
                            "developer": details.get("developer"),
                            "price": price,
                            "currency": details.get("currency"),
                            "is_free_download": is_free,
                            "rating": details.get("score"),
                            "rating_count": details.get("ratings"),
                            "installs": details.get("installs"),
                            "description": details.get("description"),
                            "app_url": details.get("url"),
                            "country": "IN",
                        })

                        seen_ids.add(app_id)
                        print(f"    PAID: {details.get('title')} | "
                              f"{price} {details.get('currency')}")

                        # Save after each confirmed paid app.
                        pd.DataFrame(records).drop_duplicates(
                            subset="app_id",
                            keep="last",
                        ).to_csv(OUTPUT_PATH, index=False)

                    except Exception as error:
                        print(f"    Could not verify {app_id}: {error}")

                    time.sleep(0.5)

                time.sleep(1)

            except Exception as error:
                print(f"  Search failed for '{query}': {error}")

    print("\nPaid-app discovery finished.")

    if records:
        final_df = pd.DataFrame(records).drop_duplicates(
            subset="app_id",
            keep="last",
        )

        final_df.to_csv(OUTPUT_PATH, index=False)

        print(f"Verified paid apps found: {len(final_df)}")
        print(f"Saved to: {OUTPUT_PATH}")
    else:
        print("No new paid apps were verified.")
        print("We may need a different discovery source or search strategy.")


if __name__ == "__main__":
    discover_paid_candidates()
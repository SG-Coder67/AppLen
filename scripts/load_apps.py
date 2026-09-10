import pandas as pd

from app.database import SessionLocal
from app.models.app import App


CSV_FILE = "data/final/apps_features.csv"


def load_apps():
    df = pd.read_csv(CSV_FILE)

    db = SessionLocal()

    try:
        for index, row in df.iterrows():

            app = App(
                # Basic information
                app_name=row["app_name"],
                category=row["category"],
                developer=row["developer"],

                # App performance
                rating=(
                    row["rating"]
                    if pd.notna(row["rating"])
                    else None
                ),

                downloads=(
                    int(row["downloads"])
                    if pd.notna(row["downloads"])
                    else None
                ),

                # Original pricing
                monthly_price=(
                    row["monthly_price"]
                    if pd.notna(row["monthly_price"])
                    else None
                ),

                yearly_price=(
                    row["yearly_price"]
                    if pd.notna(row["yearly_price"])
                    else None
                ),

                currency=(
                    row["currency"]
                    if pd.notna(row["currency"])
                    else None
                ),

                free_trial_days=(
                    int(row["free_trial_days"])
                    if pd.notna(row["free_trial_days"])
                    else None
                ),

                # Pricing information
                pricing_type=row["pricing_type"],
                pricing_source=row["pricing_source"],
                pricing_date=row["pricing_date"],
                pricing_status=row["pricing_status"],

                # Engineered features
                normalized_monthly_price=(
                    row["normalized_monthly_price"]
                    if pd.notna(row["normalized_monthly_price"])
                    else None
                ),

                normalized_yearly_price=(
                    row["normalized_yearly_price"]
                    if pd.notna(row["normalized_yearly_price"])
                    else None
                ),

                annualized_monthly_cost=(
                    row["annualized_monthly_cost"]
                    if pd.notna(row["annualized_monthly_cost"])
                    else None
                ),

                annual_savings=(
                    row["annual_savings"]
                    if pd.notna(row["annual_savings"])
                    else None
                ),

                annual_discount_pct=(
                    row["annual_discount_pct"]
                    if pd.notna(row["annual_discount_pct"])
                    else None
                ),

                downloads_numeric=(
                    row["downloads_numeric"]
                    if pd.notna(row["downloads_numeric"])
                    else None
                ),

                log_downloads=(
                    row["log_downloads"]
                    if pd.notna(row["log_downloads"])
                    else None
                ),

                popularity_score=(
                    row["popularity_score"]
                    if pd.notna(row["popularity_score"])
                    else None
                ),

                rating_score=(
                    row["rating_score"]
                    if pd.notna(row["rating_score"])
                    else None
                ),

                engagement_score=(
                    row["engagement_score"]
                    if pd.notna(row["engagement_score"])
                    else None
                ),

                price_tier=(
                    row["price_tier"]
                    if pd.notna(row["price_tier"])
                    else None
                ),

                has_free_trial=(
                    row["has_free_trial"]
                    if pd.notna(row["has_free_trial"])
                    else None
                ),

                is_freemium=(
                    row["is_freemium"]
                    if pd.notna(row["is_freemium"])
                    else None
                ),

                is_verified_price=(
                    row["is_verified_price"]
                    if pd.notna(row["is_verified_price"])
                    else None
                ),

                price_adjusted_value_score=(
                    row["price_adjusted_value_score"]
                    if pd.notna(row["price_adjusted_value_score"])
                    else None
                ),
            )

            db.add(app)
            db.commit()

            print(f"Loaded {index + 1}: {row['app_name']}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    load_apps()
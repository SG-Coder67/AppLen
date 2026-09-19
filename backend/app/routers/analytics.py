from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.app import App

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):

    total_apps = db.query(func.count(App.id)).scalar()

    total_categories = (
        db.query(func.count(func.distinct(App.category))).scalar()
    )

    average_rating = (
        db.query(func.avg(App.rating))
        .filter(App.rating.isnot(None))
        .scalar()
    )

    average_engagement = (
        db.query(func.avg(App.engagement_score))
        .filter(App.engagement_score.isnot(None))
        .scalar()
    )

    average_popularity = (
        db.query(func.avg(App.popularity_score))
        .filter(App.popularity_score.isnot(None))
        .scalar()
    )

    comparable_priced_apps = (
        db.query(func.count(App.id))
        .filter(
            App.normalized_monthly_price.isnot(None),
            App.normalized_monthly_price > 0
        )
        .scalar()
    )

    return {
        "total_apps": total_apps,
        "total_categories": total_categories,
        "average_rating": round(average_rating, 2),
        "average_engagement": round(average_engagement, 2),
        "average_popularity": round(average_popularity, 2),
        "comparable_priced_apps": comparable_priced_apps,
    }


@router.get("/categories")
def get_category_analytics(db: Session = Depends(get_db)):

    results = (
        db.query(
            App.category,
            func.count(App.id).label("app_count"),
            func.avg(App.rating).label("avg_rating"),
            func.avg(App.popularity_score).label("avg_popularity"),
            func.avg(App.engagement_score).label("avg_engagement"),
            func.avg(App.normalized_monthly_price).label("avg_monthly_price"),
        )
        .group_by(App.category)
        .order_by(func.avg(App.engagement_score).desc())
        .all()
    )

    return [
        {
            "category": row.category,
            "app_count": row.app_count,
            "avg_rating": round(row.avg_rating, 2) if row.avg_rating else None,
            "avg_popularity": round(row.avg_popularity, 2)
            if row.avg_popularity else None,
            "avg_engagement": round(row.avg_engagement, 2)
            if row.avg_engagement else None,
            "avg_monthly_price": round(row.avg_monthly_price, 2)
            if row.avg_monthly_price else None,
        }
        for row in results
    ]


@router.get("/pricing")
def get_pricing_analytics(db: Session = Depends(get_db)):

    results = (
        db.query(
            App.pricing_type,
            func.count(App.id).label("count")
        )
        .group_by(App.pricing_type)
        .order_by(func.count(App.id).desc())
        .all()
    )

    price_tiers = (
        db.query(
            App.price_tier,
            func.count(App.id).label("count")
        )
        .group_by(App.price_tier)
        .order_by(func.count(App.id).desc())
        .all()
    )

    comparable_count = (
        db.query(func.count(App.id))
        .filter(
            App.normalized_monthly_price.isnot(None),
            App.normalized_monthly_price > 0
        )
        .scalar()
    )

    return {
        "pricing_models": [
            {
                "pricing_type": row.pricing_type,
                "count": row.count
            }
            for row in results
        ],
        "price_tiers": [
            {
                "price_tier": row.price_tier,
                "count": row.count
            }
            for row in price_tiers
        ],
        "comparable_monthly_prices": comparable_count,
        "total_apps": db.query(func.count(App.id)).scalar(),
    }


@router.get("/correlations")
def get_correlations(db: Session = Depends(get_db)):

    apps = (
        db.query(
            App.rating,
            App.popularity_score,
            App.engagement_score,
            App.normalized_monthly_price,
        )
        .all()
    )

    def correlation(x, y):
        pairs = [
            (a, b)
            for a, b in zip(x, y)
            if a is not None and b is not None
        ]

        if len(pairs) < 2:
            return None

        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]

        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)

        numerator = sum(
            (a - mean_x) * (b - mean_y)
            for a, b in pairs
        )

        denominator_x = sum(
            (a - mean_x) ** 2 for a in xs
        )

        denominator_y = sum(
            (b - mean_y) ** 2 for b in ys
        )

        denominator = (denominator_x * denominator_y) ** 0.5

        if denominator == 0:
            return None

        return round(numerator / denominator, 4)

    ratings = [a.rating for a in apps]
    popularity = [a.popularity_score for a in apps]
    engagement = [a.engagement_score for a in apps]
    prices = [a.normalized_monthly_price for a in apps]

    return {
        "rating_vs_popularity": correlation(
            ratings, popularity
        ),
        "rating_vs_engagement": correlation(
            ratings, engagement
        ),
        "popularity_vs_engagement": correlation(
            popularity, engagement
        ),
        "price_vs_engagement": correlation(
            prices, engagement
        ),
    }
@router.get("/scatter")
def get_scatter_data(db: Session = Depends(get_db)):

    apps = (
        db.query(
            App.app_name,
            App.rating,
            App.popularity_score,
            App.engagement_score,
            App.normalized_monthly_price,
        )
        .all()
    )

    return [
        {
            "app_name": app.app_name,
            "rating": app.rating,
            "popularity": app.popularity_score,
            "engagement": app.engagement_score,
            "price": app.normalized_monthly_price,
        }
        for app in apps
    ]
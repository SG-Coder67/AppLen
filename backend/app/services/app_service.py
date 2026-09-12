from sqlalchemy.orm import Session

from app.models.app import App
from app.exceptions.app_exceptions import AppNotFoundException

import logging

logger = logging.getLogger(__name__)


def get_all_apps(
    db: Session,
    category: str | None = None,
    min_rating: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    limit: int = 20,
    offset: int = 0
):
    logger.info("Fetching apps")

    query = db.query(App)

    # Filters
    if category:
        query = query.filter(App.category == category)

    if min_rating is not None:
        query = query.filter(App.rating >= min_rating)

    if max_price is not None:
        query = query.filter(
            App.normalized_monthly_price <= max_price
        )
    if search:
        query = query.filter(
            App.app_name.ilike(f"%{search}%")
    )

    # Sorting
    allowed_sort_fields = {
        "id": App.id,
        "rating": App.rating,
        "downloads": App.downloads,
        "monthly_price": App.normalized_monthly_price,
        "engagement": App.engagement_score,
    }

    sort_column = allowed_sort_fields.get(sort_by, App.id)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(offset).limit(limit)

    apps = query.all()

    logger.info(f"Fetched {len(apps)} apps")

    return apps


def get_app_by_id(db: Session, app_id: int):
    logger.info(f"Fetching app with id {app_id}")

    app = db.query(App).filter(App.id == app_id).first()

    if not app:
        logger.warning(f"App not found with id {app_id}")
        raise AppNotFoundException()

    return app

def compare_apps(
    db: Session,
    app1_id: int,
    app2_id: int
):
    logger.info(
        f"Comparing apps {app1_id} and {app2_id}"
    )

    app1 = db.query(App).filter(
        App.id == app1_id
    ).first()

    app2 = db.query(App).filter(
        App.id == app2_id
    ).first()

    if not app1:
        raise AppNotFoundException()

    if not app2:
        raise AppNotFoundException()

    return {
        "app1": app1,
        "app2": app2
    }
def get_rankings(

    db: Session,

    metric: str = "engagement",

    limit: int = 10

):

    logger.info(f"Fetching rankings by {metric}")

    allowed_metrics = {

        "engagement": App.engagement_score,

        "popularity": App.popularity_score,

        "rating": App.rating,

        "value": App.price_adjusted_value_score,

    }

    sort_column = allowed_metrics.get(metric)

    if sort_column is None:

        raise ValueError("Invalid ranking metric")

    apps = (

        db.query(App)

        .filter(sort_column.isnot(None))

        .order_by(sort_column.desc())

        .limit(limit)

        .all()

    )

    logger.info(f"Fetched {len(apps)} ranked apps")

    return apps
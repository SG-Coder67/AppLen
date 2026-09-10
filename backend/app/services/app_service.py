from sqlalchemy.orm import Session

from app.models.app import App
from app.exceptions.app_exceptions import AppNotFoundException

import logging

logger = logging.getLogger(__name__)


def get_all_apps(
    db: Session,
    category: str | None = None,
    min_rating: float | None = None,
    max_price: float | None = None
):
    logger.info("Fetching apps")

    query = db.query(App)

    if category:
        query = query.filter(App.category == category)

    if min_rating is not None:
        query = query.filter(App.rating >= min_rating)

    if max_price is not None:
        query = query.filter(
            App.normalized_monthly_price <= max_price
        )

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
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.app import AppResponse, AppComparison
from app.services import app_service


router = APIRouter(
    prefix="/apps",
    tags=["Apps"]
)


@router.get("/", response_model=list[AppResponse])
def get_apps(
    category: str | None = None,
    min_rating: float | None = None,
    max_price: float | None = None,
    search: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return app_service.get_all_apps(
        db,
        category,
        min_rating,
        max_price,
        search,
        sort_by,
        order,
        limit,
        offset
    )

@router.get(
    "/compare",
    response_model=AppComparison
)
def compare_apps(
    app1_id: int,
    app2_id: int,
    db: Session = Depends(get_db)
):
    return app_service.compare_apps(
        db,
        app1_id,
        app2_id
    )
@router.get(
    "/rankings",
    response_model=list[AppResponse]
)
def get_rankings(
    metric: str = "engagement",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return app_service.get_rankings(
        db,
        metric,
        limit
    )
@router.get("/{app_id}", response_model=AppResponse)
def get_app(app_id: int, db: Session = Depends(get_db)):
    return app_service.get_app_by_id(db, app_id)

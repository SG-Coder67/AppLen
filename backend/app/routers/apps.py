from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.app import AppResponse
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
    db: Session = Depends(get_db)
):
    return app_service.get_all_apps(
        db,
        category,
        min_rating,
        max_price
    )
@router.get("/{app_id}", response_model=AppResponse)
def get_app(app_id: int, db: Session = Depends(get_db)):
    return app_service.get_app_by_id(db, app_id)
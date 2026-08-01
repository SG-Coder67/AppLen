from app.database import SessionLocal 
from app.models.app import App
from app.schemas.app import AppCreate,AppResponse
from sqlalchemy import select
from fastapi import HTTPException,APIRouter,Depends
from app.dependencies import get_db
from sqlalchemy.orm import Session
from app.services import app_service
router=APIRouter(
    prefix="/apps",
    tags=["Apps"]
)

@router.post("",response_model=AppResponse)
def create_app(app:AppCreate,db:Session=Depends(get_db)):
    return app_service.create_app(db,app)
@router.get("", response_model=list[AppResponse])
def get_apps(db: Session = Depends(get_db)):
    return app_service.get_all_apps(db)
@router.get("/{app_id}", response_model=AppResponse)
def get_app(app_id: int, db: Session = Depends(get_db)):
    return app_service.get_app_by_id(db, app_id)
@router.put("/{app_id}", response_model=AppResponse)
def update_app(app_id: int,app: AppCreate,db: Session = Depends(get_db)):
    return app_service.update_app(db, app_id, app)
@router.delete("/{app_id}")
def delete_app(app_id: int, db: Session = Depends(get_db)):
    return app_service.delete_app(db, app_id)
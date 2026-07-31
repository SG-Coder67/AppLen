from app.database import SessionLocal 
from app.models.app import App
from app.schemas.app import AppCreate,AppResponse
from sqlalchemy import select
from fastapi import HTTPException,APIRouter,Depends
from app.dependencies import get_db
from sqlalchemy.orm import Session
router=APIRouter(
    prefix="/apps",
    tags=["Apps"]
)

@router.post("",response_model=AppResponse)
def create_app(app:AppCreate,session:Session=Depends(get_db)):
    db_app=App(name=app.name,price=app.price)
    session.add(db_app)
    session.commit()
    session.refresh(db_app)
    return db_app
@router.get("",response_model=list[AppResponse])
def get_apps(session:Session=Depends(get_db)):
    apps=session.scalars(select(App)).all()
    return apps
@router.get("/{app_id}",response_model=AppResponse)
def get_apps_id(app_id:int,session:Session=Depends(get_db)):
    app=session.scalar(select(App).where(App.id==app_id))
    if app is None:
        raise HTTPException(
            status_code=404,
            detail="App not found"
            )
    return app
@router.put("/{app_id}",response_model=AppResponse)
def update_app(app_id:int,app:AppCreate,session:Session=Depends(get_db)):
    db_app=session.scalar(select(App).where(App.id==app_id))
    if db_app is None:
        raise HTTPException(
            status_code=404,
            detail="No Updation"
            )
    db_app.name=app.name
    db_app.price=app.price
    session.commit()
    session.refresh(db_app)
    return db_app
@router.delete("/{app_id}")
def delete_app(app_id: int,session:Session=Depends(get_db)):
    db_app=session.scalar(select(App).where(App.id == app_id))
    if db_app is None:
        raise HTTPException(
            status_code=404,
            detail="App not found"
        )
    session.delete(db_app)
    session.commit()
    return{
        "message":"App deleted successfully"
    }
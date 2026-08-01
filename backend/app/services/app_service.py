from sqlalchemy.orm import Session
from app.models.app import App
from app.schemas.app import AppCreate
from fastapi import HTTPException
def create_app(db:Session,app:AppCreate):
    existing_app = db.query(App).filter(App.name == app.name).first()
    if existing_app:
        raise HTTPException(
            status_code=400,
            detail="App already exists"
        )
    db_app=App(name=app.name,price=app.price)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app
def get_all_apps(db: Session):
    return db.query(App).all()
def get_app_by_id(db: Session, app_id: int):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="App not found"
        )
    return app
def update_app(db: Session, app_id: int, updated_app: AppCreate):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="App not found"
        )
    app.name = updated_app.name
    app.price = updated_app.price
    db.commit()
    db.refresh(app)
    return app
def delete_app(db: Session, app_id: int):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=404,
            detail="App not found"
        )
    db.delete(app)
    db.commit()
    return {
        "message": "App deleted successfully"
    }
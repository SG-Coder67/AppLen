from sqlalchemy.orm import Session
from app.models.app import App
from app.schemas.app import AppCreate
from app.exceptions.app_exceptions import (AppAlreadyExistsException,AppNotFoundException)
import logging
logger = logging.getLogger(__name__)
def create_app(db:Session,app:AppCreate):
    logger.info(f"Creating app: {app.name}")
    existing_app = db.query(App).filter(App.name == app.name).first()
    if existing_app:
        logger.warning(f"App already exists: {app.name}")
        raise AppAlreadyExistsException()
    db_app=App(name=app.name,price=app.price)
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    logger.info(f"App created successfully with id {db_app.id}")
    return db_app
def get_all_apps(db: Session):
    return db.query(App).all()
def get_app_by_id(db: Session, app_id: int):
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        logger.warning(f"App not found with id {app_id}")
        raise AppNotFoundException()
    return app
def update_app(db: Session, app_id: int, updated_app: AppCreate):
    logger.info(f"Updating app with id {app_id}")
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        logger.warning(f"App not found with id {app_id}")
        raise AppNotFoundException()
    app.name = updated_app.name
    app.price = updated_app.price
    db.commit()
    db.refresh(app)
    logger.info(f"App {app_id} updated successfully")
    return app
def delete_app(db: Session, app_id: int):
    logger.info(f"Deleting app with id {app_id}")
    app = db.query(App).filter(App.id == app_id).first()
    if not app:
        logger.warning(f"App not found with id {app_id}")
        raise AppNotFoundException()
    db.delete(app)
    db.commit()
    logger.info(f"App {app_id} deleted successfully")
    return {
        "message": "App deleted successfully"
    }
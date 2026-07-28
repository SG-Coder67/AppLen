from fastapi import FastAPI
from app.database import Base, engine, SessionLocal 
from app.models.app import App
from app.schemas.app import AppCreate,AppResponse
from sqlalchemy import select
from fastapi import HTTPException
Base.metadata.create_all(bind=engine)
app=FastAPI(title="AppLen API")
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}
@app.post("/apps",response_model=AppResponse)
def create_app(app:AppCreate):
    session=SessionLocal()
    try:
        db_app=App(name=app.name,price=app.price)
        session.add(db_app)
        session.commit()
        session.refresh(db_app)
        return db_app
    finally:
        session.close()
@app.get("/apps",response_model=list[AppResponse])
def get_apps():
    session=SessionLocal()
    try:
        apps=session.scalars(select(App)).all()
        return apps
    finally:
        session.close()
@app.get("/apps/{app_id}",response_model=AppResponse)
def get_apps_id(app_id:int):
    session=SessionLocal()
    try:
        app=session.scalar(select(App).where(App.id==app_id))
        if app is None:
            raise HTTPException(
                status_code=404,
                detail="App not found"
            )
        return app
    finally:
        session.close()
@app.put("/apps/{app_id}",response_model=AppResponse)
def update_app(app_id:int,app:AppCreate):
    session=SessionLocal()
    try:
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
    finally:
        session.close()
@app.delete("/apps/{app_id}")
def delete_app(app_id: int):
    session=SessionLocal()
    try:
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
    finally:
        session.close()
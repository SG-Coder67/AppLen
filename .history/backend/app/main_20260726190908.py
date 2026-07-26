from fastapi import FastAPI
from app.database import Base, engine, SessionLocal 
from app.models.app import App
from app.schemas.app import AppCreate
Base.metadata.create_all(bind=engine)
app=FastAPI(title="AppLen API")
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}
@app.post("/apps")
def create_app(app:AppCreate):
    session=SessionLocal()
    db_app=App(name=app.name,price=app.price)
    session.add(db_app)
    session.commit()
    session.refresh(db_app)
    session.close()
    return db_app
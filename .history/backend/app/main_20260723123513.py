from fastapi import FastAPI
from app.database import Base, engine
from app.models.app import App
Base.metadata.create_all(bind=engine)
app=FastAPI(title="AppLen API");
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}
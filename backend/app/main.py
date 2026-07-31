from fastapi import FastAPI
from app.routers import apps
from app.database import Base, engine
app=FastAPI(title="AppLen API")
Base.metadata.create_all(bind=engine)
app.include_router(apps.router)
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}

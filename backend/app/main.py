from fastapi import FastAPI
from app.routers import apps
from app.database import Base, engine
from app.exceptions.app_exceptions import (
    AppAlreadyExistsException,
    AppNotFoundException,
)
from app.exceptions.exception_handlers import (
    app_already_exists_handler,
    app_not_found_handler,
)
from app.utils import logging_config
app=FastAPI(title="AppLen API")
app.add_exception_handler(
    AppAlreadyExistsException,
    app_already_exists_handler,
)

app.add_exception_handler(
    AppNotFoundException,
    app_not_found_handler,
)
app.include_router(apps.router)
@app.get("/")
def root():
    return {"message": "Welcome to AppLen API"}

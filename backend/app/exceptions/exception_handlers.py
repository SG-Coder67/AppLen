from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.app_exceptions import (
    AppAlreadyExistsException,
    AppNotFoundException,
)


async def app_already_exists_handler(
    request: Request,
    exc: AppAlreadyExistsException,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "App already exists"},
    )


async def app_not_found_handler(
    request: Request,
    exc: AppNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={"detail": "App not found"},
    )
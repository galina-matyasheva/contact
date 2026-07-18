import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.strings import APP_DESCRIPTION
from app.core.exceptions import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.core.logging import setup_logging
from app.middleware.cors import setup_cors
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.routers import contact, health, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.DATA_DIR)
    logger = logging.getLogger(__name__)
    logger.info("Запуск %s v%s", settings.APP_NAME, settings.APP_VERSION)
    yield
    logger.info("Остановка приложения")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
setup_cors(app)

app.include_router(contact.router)
app.include_router(health.router)
app.include_router(metrics.router)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

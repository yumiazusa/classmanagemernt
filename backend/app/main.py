from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base_class import Base
from app.db.init_db import (
    ensure_database_exists,
    ensure_default_docs,
)
from app.db.session import engine

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)


@app.on_event("startup")
def startup_db_sync() -> None:
    ensure_database_exists()
    Base.metadata.create_all(bind=engine)
    ensure_default_docs()


app.include_router(api_router)

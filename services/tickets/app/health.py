import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import engine

router = APIRouter()
log = logging.getLogger("uvicorn.error")

def check_database():
    with engine.connect() as connection:
        for table in ("vehicles", "tickets", "members"):
            connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))

@asynccontextmanager
async def lifespan(app):
    for attempt in range(60):
        try:
            await asyncio.to_thread(check_database)
            break
        except SQLAlchemyError:
            if attempt == 59:
                raise RuntimeError("Base de datos o esquema no disponible tras 120 segundos") from None
            log.warning("Esperando base de datos y esquema (%s/60)", attempt + 1)
            await asyncio.sleep(2)
    yield
    engine.dispose()

@router.get("/health")
def health():
    return {"status": "ok", "version": os.getenv("APP_VERSION", "local")}

@router.get("/ready")
def ready():
    try:
        check_database()
    except SQLAlchemyError:
        raise HTTPException(503, "Base de datos no disponible") from None
    return {"status": "ready"}

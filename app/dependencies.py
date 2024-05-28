# app/dependencies.py
from typing import Generator
from app.db.session import SessionLocal

async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session

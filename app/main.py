import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.fetch_rss_feeds import fetch_rss_feeds
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from sqlalchemy import text
import joblib
import os

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 스케쥴러 설정
scheduler = AsyncIOScheduler()
scheduler.add_job(fetch_rss_feeds, 'cron', hour=0, minute=0)
scheduler.start()

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# async def fetch_titles():
#     model_path = os.path.join("app", "text_classification_model.pkl")
#     model = joblib.load(model_path)
    
#     async with SessionLocal() as session:
#         result = await session.execute(text("SELECT title FROM items"))
#         titles = result.fetchall()
#         predictions = model.predict([title[0] for title in titles])
#         result = predictions.tolist()
#         print(result)

# @app.on_event("startup")
# async def startup_event():
#     # 앱 시작 시 한 번 실행
#     await fetch_titles()

def start_uvicorn():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

def main():
    start_uvicorn()

if __name__ == "__main__":
    main()

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
from app.utils.fetch_rss_feeds import fetch_rss_feeds
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 스케쥴러 매일 새벽 2시에 실행
korea_timezone = pytz.timezone("Asia/Seoul")

scheduler = AsyncIOScheduler()
scheduler.add_job(
    fetch_rss_feeds, CronTrigger(hour=2, minute=0, timezone=korea_timezone)
)
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


# @app.on_event("startup")
# async def startup_event():
#     # 앱 시작 시 한 번 실행
#     await fetch_rss_feeds()


def start_uvicorn():
    import uvicorn

    # 30009 포트로 변경
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


def main():
    start_uvicorn()


if __name__ == "__main__":
    main()

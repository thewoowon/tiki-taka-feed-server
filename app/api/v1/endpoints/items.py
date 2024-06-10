from fastapi import APIRouter
from app.utils.refresh_rss_feeds import refresh_rss_feeds
from app.db.session import SessionLocal


router = APIRouter()


@router.get("/")
async def read_items():
    async with SessionLocal() as session:
        # feed 테이블에서 10개만 가져오기
        result = await session.execute("SELECT * FROM feed LIMIT 10")
        items = result.fetchall()
        return items


@router.post("/refresh")
async def refresh():
    # 모든 items를 삭제하고 다시 생성
    await refresh_rss_feeds()
    return True

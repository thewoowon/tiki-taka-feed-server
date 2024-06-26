import feedparser
import datetime
from sqlalchemy import text
from app.db.session import SessionLocal
import re
import requests
from bs4 import BeautifulSoup


feed_urls = [
    "https://www.mobiinside.co.kr/feed",
    "https://www.dailytrend.co.kr/feed",
    "https://servicedesign.tistory.com/feed",
    "https://blog.opensurvey.co.kr/feed",
    "https://techblog.woowahan.com/feed",
    "https://blog.rss.naver.com/businessinsight.xml",
    "https://toss.tech/rss.xml",
    "https://wp.outstanding.kr/feed",
    "https://yozm.wishket.com/magazine/feed",
    "https://platum.kr/feed",
    "https://uppity.co.kr/feed",
    "https://www.bespinglobal.com/feed",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCQ2DWm5Md16Dc3xRwwhVE7Q",
]


def get_thumbnail_from_meta(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    meta_tag = soup.find("meta", property="og:image")
    if meta_tag:
        return meta_tag["content"]
    return ""


def generate_insert_query(entry, company_id):
    fields = [
        "title",
        "description",
        "link",
        "thumbnail",
        "published",
        "guid",
        "company_id",
    ]
    values = {field: entry.get(field, "") for field in fields}
    values["company_id"] = company_id  # Ensure company_id is set correctly

    # published 필드를 datetime 형식으로 변환
    if "published_parsed" in entry:
        values["published"] = datetime.datetime(*entry.published_parsed[:6])

    return fields, values


async def fetch_rss_feeds():
    today = datetime.date.today()
    day_before = today - datetime.timedelta(days=1)
    tm_year, tm_mon, tm_mday = day_before.year, day_before.month, day_before.day

    async with SessionLocal() as session:
        for idx, url in enumerate(feed_urls):
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if "published_parsed" not in entry or entry.published_parsed is None:
                    entry["published_parsed"] = datetime.datetime.now().timetuple()
                if (
                    entry.published_parsed.tm_year >= tm_year
                    and entry.published_parsed.tm_mon >= tm_mon
                    and entry.published_parsed.tm_mday >= tm_mday
                ):

                    # guid로 중복 체크
                    guid = entry.get("guid", "")
                    exists = await session.execute(
                        text("SELECT id FROM feed WHERE guid = :guid"),
                        {"guid": guid},
                    )
                    if exists.scalar():
                        continue

                    if "description" not in entry or entry.description is None:
                        entry["description"] = ""
                    else:
                        # 정규식으로 모든 쌍따옴표 제거
                        entry["description"] = re.sub(r'"', "", entry["description"])
                        entry["description"] = entry["description"][:100]

                    thumbnail_url = entry.get("media_thumbnail", [{"url": None}])[0][
                        "url"
                    ]
                    if not thumbnail_url:  # 썸네일 URL이 없으면 메타 데이터에서 추출
                        thumbnail_url = get_thumbnail_from_meta(entry.link)
                    entry["thumbnail"] = thumbnail_url

                    fields, values = generate_insert_query(entry, idx + 1)
                    insert_query = text(
                        f"""
                        INSERT INTO feed ({", ".join(fields)})
                        VALUES ({", ".join([f":{field}" for field in fields])})
                    """
                    )
                    await session.execute(insert_query, values)

        await session.commit()

    return True

import feedparser
import datetime
import os
import joblib
from sqlalchemy import text
from app.db.session import SessionLocal
import re

job_tags = {
    "FE": 1,
    "BE": 2,
    "DEVOPS": 3,
    "SECURITY": 4,
    "DATA": 5,
    "AI": 6,
    "LLM": 7,
    "BLOCKCHAIN": 8,
    "ETC": 9,
}

skill_tags = {
    "TYPESCRIPT": 1,
    "PYTHON": 2,
    "KOTLIN": 3,
    "GO": 4,
    "RUBY": 5,
    "C++": 6,
    "C": 7,
    "JAVA": 8,
    "C#": 9,
    "PHP": 10,
    "ETC": 11,
}

feed_urls = [
    # 카카오
    "https://tech.kakao.com/blog/feed",
    # 왓챠
    "https://medium.com/feed/watcha",
    # 컬리
    "https://helloworld.kurly.com/feed",
    # 우아한형제들
    "https://techblog.woowahan.com/feed",
    # 뱅크샐러드
    "https://blog.banksalad.com/rss.xml",
    # NHN
    "https://meetup.nhncloud.com/rss",
    # 하이퍼커넥트
    "https://hyperconnect.github.io/feed",
    # 요기요
    "https://techblog.yogiyo.co.kr/feed",
    # 이스트소프트
    "https://blog.est.ai/feed",
    # 플랫팜
    "https://medium.com/feed/platfarm",
    # 스포카
    "https://spoqa.github.io/rss",
    # 네이버플레이스
    "https://medium.com/feed/naver-place-dev",
    # 라인
    "https://engineering.linecorp.com/ko/feed/index.html",
    # 리디
    "https://www.ridicorp.com/feed",
    # 네이버
    "https://d2.naver.com/d2.atom",
    # 데보션
    "https://devocean.sk.com/blog/rss.do",
    # 구글코리아
    "https://feeds.feedburner.com/GoogleDevelopersKorea",
    # AWS코리아
    "https://aws.amazon.com/ko/blogs/tech/feed",
    # 데이블
    "https://teamdable.github.io/techblog/feed",
    # 토스
    "https://toss.tech/rss.xml",
    # 스마일게이트
    "https://smilegate.ai/recent/feed",
    # 롯데온
    "https://techblog.lotteon.com/feed",
    # 카카오엔터프라이즈
    "https://tech.kakaoenterprise.com/feed",
    # 메가존클라우드
    "https://www.megazone.com/blog/feed",
    # SKC&C
    "https://engineering-skcc.github.io/feed.xml",
    # 여기어때
    "https://techblog.gccompany.co.kr/feed",
    # 원티드
    "https://medium.com/feed/wantedjobs",
    # 비브로스
    "https://boostbrothers.github.io/rss",
    # 포스타입
    "https://team.postype.com/rss",
    # 지마켓
    "https://dev.gmarket.com/feed",
    # SK플래닛
    "https://techtopic.skplanet.com/rss",
    # AB180
    "https://raw.githubusercontent.com/ab180/engineering-blog-rss-scheduler/main/rss.xml",
    # 데브시스터즈
    "https://tech.devsisters.com/rss.xml",
    # 넷마블
    "https://netmarble.engineering/feed",
    # 마키나락스
    "https://www.makinarocks.ai/blog/feed",
    # 드라마앤컴패니
    "https://blog.dramancompany.com/feed",
    # 티몬
    "https://rss.blog.naver.com/tmondev.xml",
    # 루닛
    "https://medium.com/feed/lunit",
    # 인프런
    "https://tech.inflab.com/rss.xml",
    # 게임빌컴투스플랫폼
    "https://on.com2us.com/tag/기술블로그/feed",
    # 카카오페이
    "https://tech.kakaopay.com/rss",
    # 덴티움
    "https://www.dentium.tech/rss.xml",
    # 사람인
    "https://saramin.github.io/feed",
    # 올리브영
    "https://oliveyoung.tech/rss.xml",
    # 티빙
    "https://medium.com/feed/tving-team",
    # 11번가
    "https://11st-tech.github.io/rss",
    # 다나와
    "https://danawalab.github.io/feed",
    # 농심
    "https://tech.cloud.nongshim.co.kr/feed",
    # 트렌비
    "https://tech.trenbe.com/feed",
    # 교보DTS
    "https://blog.kyobodts.co.kr/feed",
    # 중고나라
    "https://teamblog.joonggonara.co.kr/feed",
    # 씨에스리
    "https://blog.cslee.co.kr/feed",
    # 글루시스
    "https://tech.gluesys.com/feed",
    # DND
    "https://blog.dnd.ac/feed",
    # LG유플러스
    "https://techblog.uplus.co.kr/feed",
]

def generate_insert_query(entry, feed_id):
    fields = ["title", "description", "link", "thumbnail", "published", "guid", "feed_id"]
    values = {field: entry.get(field, "") for field in fields}
    values["feed_id"] = feed_id  # Ensure feed_id is set correctly

    # published 필드를 datetime 형식으로 변환
    if "published_parsed" in entry:
        values["published"] = datetime.datetime(*entry.published_parsed[:6])

    return fields, values

async def fetch_rss_feeds():
    today = datetime.date.today()
    day_before = today - datetime.timedelta(days=1)
    tm_year, tm_mon, tm_mday = day_before.year, day_before.month, day_before.day
    day_before_datetime = datetime.datetime(tm_year, tm_mon, tm_mday)

    model_path = os.path.join("app", "text_classification_model.pkl")
    model = joblib.load(model_path)

    async with SessionLocal() as session:
        insert_queries_array = []
        for idx, url in enumerate(feed_urls):
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if "published_parsed" not in entry or entry.published_parsed is None:
                    continue
                if (entry.published_parsed.tm_year >= tm_year and
                    entry.published_parsed.tm_mon >= tm_mon and
                    entry.published_parsed.tm_mday >= tm_mday):
                    
                    if "description" not in entry or entry.description is None:
                        entry["description"] = ""
                    else:
                        #정규식으로 모든 쌍따옴표 제거
                        entry["description"] = re.sub(r'"', '', entry["description"])
                        entry["description"] = entry["description"][:100]

                    fields, values = generate_insert_query(entry, idx + 1)
                    insert_query = text(f"""
                        INSERT INTO items ({", ".join(fields)})
                        VALUES ({", ".join([f":{field}" for field in fields])})
                    """)
                    await session.execute(insert_query, values)
                    predictions = model.predict([entry.title])
                    result = predictions.tolist()

        await session.commit()

        rows = await session.execute(
            text("SELECT * FROM items WHERE published >= :published"),
            {"published": day_before_datetime}
        )
        items = rows.fetchall()
        
        insert_tags_array = []
        insert_jobs_array = []
        
        for row in items:
            predictions = model.predict([row.title])
            result = predictions.tolist()[0]
            
            insert_tags_array.append({
                "item_id": row.id,
                "job_tag_id": job_tags.get(result[0], 1)  # 기본값으로 1 사용
            })
            insert_jobs_array.append({
                "item_id": row.id,
                "skill_tag_id": skill_tags.get(result[1], 1)  # 기본값으로 1 사용
            })

        if insert_tags_array:
            insert_tags_query = text("""
                INSERT INTO item_job_tags (item_id, job_tag_id)
                VALUES (:item_id, :job_tag_id)
            """)
            await session.execute(insert_tags_query, insert_tags_array)

        if insert_jobs_array:
            insert_jobs_query = text("""
                INSERT INTO item_skill_tags (item_id, skill_tag_id)
                VALUES (:item_id, :skill_tag_id)
            """)
            await session.execute(insert_jobs_query, insert_jobs_array)

        await session.commit()
        
    return True

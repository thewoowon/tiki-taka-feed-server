import feedparser
import datetime
from app.dependencies import get_db
import os
import joblib
from sqlalchemy import text


feed_urls = [
    # 카카오
    "https://tech.kakao.com/blog/feed",
    # 왓챠
    "https://medium.com/feed/watcha",
    # 컬리
    "https://helloworld.kurly.com/feed",
    # # 우아한형제들
    # "https://techblog.woowahan.com/feed",
    # # 뱅크샐러드
    # "https://blog.banksalad.com/rss.xml",
    # # NHN
    # "https://meetup.nhncloud.com/rss",
    # # 하이퍼커넥트
    # "https://hyperconnect.github.io/feed",
    # # 요기요
    # "https://techblog.yogiyo.co.kr/feed",
    # # 이스트소프트
    # "https://blog.est.ai/feed",
    # # 플랫팜
    # "https://medium.com/feed/platfarm",
    # # 스포카
    # "https://spoqa.github.io/rss",
    # # 네이버플레이스
    # "https://medium.com/feed/naver-place-dev",
    # # 라인
    # "https://engineering.linecorp.com/ko/feed/index.html",
    # # 리디
    # "https://www.ridicorp.com/feed",
    # # 네이버
    # "https://d2.naver.com/d2.atom",
    # # 데보션
    # "https://devocean.sk.com/blog/rss.do",
    # # 구글코리아
    # "https://feeds.feedburner.com/GoogleDevelopersKorea",
    # # AWS코리아
    # "https://aws.amazon.com/ko/blogs/tech/feed",
    # # 데이블
    # "https://teamdable.github.io/techblog/feed",
    # # 토스
    # "https://toss.tech/rss.xml",
    # # 스마일게이트
    # "https://smilegate.ai/recent/feed",
    # # 롯데온
    # "https://techblog.lotteon.com/feed",
    # # 카카오엔터프라이즈
    # "https://tech.kakaoenterprise.com/feed",
    # # 메가존클라우드
    # "https://www.megazone.com/blog/feed",
    # # SKC&C
    # "https://engineering-skcc.github.io/feed.xml",
    # # 여기어때
    # "https://techblog.gccompany.co.kr/feed",
    # # 원티드
    # "https://medium.com/feed/wantedjobs",
    # # 비브로스
    # "https://boostbrothers.github.io/rss",
    # # 포스타입
    # "https://team.postype.com/rss",
    # # 지마켓
    # "https://dev.gmarket.com/feed",
    # # SK플래닛
    # "https://techtopic.skplanet.com/rss",
    # # AB180
    # "https://raw.githubusercontent.com/ab180/engineering-blog-rss-scheduler/main/rss.xml",
    # # 데브시스터즈
    # "https://tech.devsisters.com/rss.xml",
    # # 넷마블
    # "https://netmarble.engineering/feed",
    # # 마키나락스
    # "https://www.makinarocks.ai/blog/feed",
    # # 드라마앤컴패니
    # "https://blog.dramancompany.com/feed",
    # # 티몬
    # "https://rss.blog.naver.com/tmondev.xml",
    # # 루닛
    # "https://medium.com/feed/lunit",
    # # 인프런
    # "https://tech.inflab.com/rss.xml",
    # # 게임빌컴투스플랫폼
    # "https://on.com2us.com/tag/기술블로그/feed",
    # # 카카오페이
    # "https://tech.kakaopay.com/rss",
    # # 덴티움
    # "https://www.dentium.tech/rss.xml",
    # # 사람인
    # "https://saramin.github.io/feed",
    # # 올리브영
    # "https://oliveyoung.tech/rss.xml",
    # # 티빙
    # "https://medium.com/feed/tving-team",
    # # 11번가
    # "https://11st-tech.github.io/rss",
    # # 다나와
    # "https://danawalab.github.io/feed",
    # # 농심
    # "https://tech.cloud.nongshim.co.kr/feed",
    # # 트렌비
    # "https://tech.trenbe.com/feed",
    # # 교보DTS
    # "https://blog.kyobodts.co.kr/feed",
    # # 중고나라
    # "https://teamblog.joonggonara.co.kr/feed",
    # # 씨에스리
    # "https://blog.cslee.co.kr/feed",
    # # 글루시스
    # "https://tech.gluesys.com/feed",
    # # DND
    # "https://blog.dnd.ac/feed",
    # # LG유플러스
    # "https://techblog.uplus.co.kr/feed",
]


async def fetch_rss_feeds():
    # 오늘 날짜 가져오기
    today = datetime.datetime.now()
    tm_year = today.year
    tm_mon = today.month
    tm_mday = today.day
    db = get_db()

    entries = []
    for idx, url in enumerate(feed_urls):
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # 오늘 날짜 이후의 글만 가져오기
            # 키가 없는 경우가 있어서 예외처리
            print(entry)
            if "published_parsed" not in entry:
                continue
            if entry.published_parsed is None:
                continue
            if (
                entry.published_parsed.tm_year >= tm_year
                and entry.published_parsed.tm_mon >= tm_mon
                and entry.published_parsed.tm_mday >= tm_mday
            ):
                print(entry.title, entry.published_parsed)
                entries.append({"title": entry.title, "description": entry.description})

    model_path = os.path.join("app", "text_classification_model.pkl")
    model = joblib.load(model_path)
    predictions = model.predict([entry["title"] for entry in entries])
    result = predictions.tolist()
    
    
    # result는 2차원 배열이므로 1차원 배열로 변환
    result = [item for sublist in result for item in sublist]
    # DB에 저장


    return entries

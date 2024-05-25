import feedparser

def fetch_rss_feeds(feed_urls):
    entries = []
    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entries.append({
                'title': entry.title,
                'description': entry.description
            })
    return entries

feed_urls = [
    "http://example.com/rss1",
    "http://example.com/rss2",
    # 추가할 RSS 피드 URL
]

entries = fetch_rss_feeds(feed_urls)

# 카테고리 결과 출력
for idx, entry in enumerate(entries):
    print(f"Title: {entry['title']}\nDescription: {entry['description']}")

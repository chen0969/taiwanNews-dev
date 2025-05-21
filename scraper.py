import feedparser
import json
from datetime import datetime

# Google News RSS feed：搜尋「Taiwan」，地區為加拿大
rss_url = "https://news.google.com/rss/search?q=Taiwan+when:7d&hl=en-CA&gl=CA&ceid=CA:en"

feed = feedparser.parse(rss_url)

articles = []
for entry in feed.entries:
    # 將 published 轉為 ISO 日期格式
    try:
        published_parsed = entry.published_parsed
        published_iso = datetime(*published_parsed[:6]).isoformat()
        published_date = datetime(*published_parsed[:3]).strftime("%Y-%m-%d")
    except:
        published_iso = None
        published_date = "未知日期"

    articles.append({
        "title": entry.title,
        "url": entry.link,
        "published": published_iso,
        "date": published_date
    })

news_data = {
    "source": "Google News RSS",
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles,
}

# 儲存為 data/news.json
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

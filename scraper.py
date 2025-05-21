import feedparser
import json
from datetime import datetime

# Google News RSS feed (限制地區為加拿大，搜尋「台灣」)
rss_url = "https://news.google.com/rss/search?q=Taiwan+when:7d&hl=en-CA&gl=CA&ceid=CA:en"

feed = feedparser.parse(rss_url)

articles = []
for entry in feed.entries:
    articles.append({
        "title": entry.title,
        "link": entry.link,
        "published": entry.published if "published" in entry else None
    })

news_data = {
    "source": "Google News RSS",
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles
}

# 儲存為 data/news.json
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

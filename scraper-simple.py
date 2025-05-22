import feedparser
import json
from datetime import datetime, timedelta

# Google News RSS feed（搜尋 Taiwan，地區：加拿大）
rss_url = "https://news.google.com/rss/search?q=Taiwan&hl=en-CA&gl=CA&ceid=CA:en"

feed = feedparser.parse(rss_url)

articles = []
now = datetime.utcnow()
cutoff = now - timedelta(days=1)  # 24 小時內

for entry in feed.entries:
    try:
        published_parsed = entry.published_parsed
        published_dt = datetime(*published_parsed[:6])

        if published_dt >= cutoff:
            articles.append({
                "source": "Google News (Taiwan)",
                "title": entry.title,
                "url": entry.link,
                "published": published_dt.isoformat(),
                "date": published_dt.strftime("%Y-%m-%d")
            })
    except Exception as e:
        print("跳過無效項目:", e)
        continue

# 時間排序
articles.sort(key=lambda x: x["published"], reverse=True)

news_data = {
    "source": "Google News RSS",
    "query": "Taiwan",
    "updated_at": now.isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles
}

# 儲存為 data/news.json
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

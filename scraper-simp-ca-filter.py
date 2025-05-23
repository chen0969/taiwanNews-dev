import feedparser
import json
from datetime import datetime, timedelta

# Google News RSS feed（搜尋 Taiwan，地區：加拿大）
rss_url = "https://news.google.com/rss/search?q=Taiwan&hl=en-CA&gl=CA&ceid=CA:en"
feed = feedparser.parse(rss_url)

# 加拿大媒體關鍵字清單
canadian_media_keywords = [
    "CBC", "Radio-Canada", "Global News", "CTV News", "National Post",
      "Canadian Press", "APTN", "CPAC", "Ottawa Citizen", "Ottawa Sun",
      "CityNews", "Hill Times", "Ottawa Business Journal", "Daily Courier",
      "Penticton Herald", "The Intelligencer", "Brantford Expositor",
      "Recorder and Times", "Chatham Daily News", "Standard Freeholder",
      "Journal de Québec", "La Tribune", "Le Nouvelliste", "Le Quotidien",
      "The Guardian", "Journal Pioneer", "Western Star", "Evening News",
      "Sault Star", "Sudbury Star"
]

articles = []
now = datetime.utcnow()
cutoff = now - timedelta(days=1)  # 限制為 24 小時內

for entry in feed.entries:
    try:
        published_parsed = entry.published_parsed
        published_dt = datetime(*published_parsed[:6])

        if published_dt >= cutoff:
            # 判斷 title 中是否有出現加拿大媒體關鍵字
            title_lower = entry.title.lower()
            matched_source = None
            for keyword in canadian_media_keywords:
                if keyword.lower() in title_lower:
                    matched_source = keyword
                    break
            source = matched_source if matched_source else "Google News"

            articles.append({
                "source": source,
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

# 結果格式
news_data = {
    "source": "Google News RSS",
    "query": "Taiwan",
    "updated_at": now.isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles
}

# 儲存為 JSON 檔案
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

import feedparser
import json
from datetime import datetime, timedelta
import time

# 加拿大媒體清單（可每分鐘輪流處理一個）
canadian_sources = [
    "CBC", "Global News", "CTV News", "National Post", "Ottawa Citizen",
    "Ottawa Sun", "CityNews", "Hill Times", "BNN Bloomberg",
    "Canadaland", "iPolitics", "The Globe and Mail"
]

# Google News RSS 建構 URL
def build_rss_url(source):
    return f"https://news.google.com/rss/search?q=Taiwan+source:{source.replace(' ', '+')}&hl=en-CA&gl=CA&ceid=CA:en"

# 解析 RSS 並擷取新聞（僅限近 24 小時）
def fetch_articles(source):
    feed = feedparser.parse(build_rss_url(source))
    now = datetime.utcnow()
    cutoff = now - timedelta(days=1)
    articles = []

    if not feed.entries:
        print(f"⚠️ {source}: 無資料")
        return []

    for entry in feed.entries:
        try:
            pub = datetime(*entry.published_parsed[:6])
            if pub >= cutoff:
                articles.append({
                    "source": source,
                    "title": entry.title,
                    "url": entry.link,
                    "published": pub.isoformat(),
                    "date": pub.strftime("%Y-%m-%d")
                })
        except Exception as e:
            continue
    return articles

# 去除重複（依 title + url）
def deduplicate(articles):
    seen = set()
    unique = []
    for a in articles:
        key = (a["title"], a["url"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique

# 主執行邏輯（模擬一輪所有來源，部署時可改為每分鐘跑一個）
all_articles = []
for source in canadian_sources:
    print(f"🔍 抓取中：{source}")
    all_articles.extend(fetch_articles(source))
    time.sleep(1)  # 模擬「每分鐘輪流處理一個媒體」

# 整理結果
final_articles = deduplicate(all_articles)
final_articles.sort(key=lambda x: x["published"], reverse=True)

news_data = {
    "source": "Google News RSS + Filtered Sources",
    "query": "Taiwan",
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "article_count": len(final_articles),
    "articles": final_articles
}

# 儲存到 data/news.json
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"✅ 已抓取並儲存 {len(final_articles)} 則新聞到 data/news.json")

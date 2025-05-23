import feedparser
import json
from datetime import datetime, timedelta
import time

# 設定要搜尋的來源媒體與關鍵字
canadian_sources = [
    "CBC", "Global News", "CTV News", "National Post", "Ottawa Citizen",
    "Ottawa Sun", "CityNews", "Hill Times", "BNN Bloomberg",
    "Canadaland", "iPolitics", "The Globe and Mail", "Financial Post", "Maclean's", "The Canadian Press",
    "La Presse", "Vice Canada", "The Logic", "The Conversation Canada", "PressProgress", "Ottawa Matters", 
    "Ottawa Business Journal", "Ottawa Life Magazine"
]

search_keywords = [
    "Taiwan", "China", "Lai Ching-te", "William Lai"
]

# Google News RSS 建構 URL
def build_rss_url(source, keyword):
    return f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}+source:{source.replace(' ', '+')}&hl=en-CA&gl=CA&ceid=CA:en"

# 擷取新聞資料（24小時內）
def fetch_articles(source, keyword):
    feed = feedparser.parse(build_rss_url(source, keyword))
    now = datetime.utcnow()
    cutoff = now - timedelta(days=1)
    articles = []

    if not feed.entries:
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
        except Exception:
            continue
    return articles

# 去除重複（title + url）
def deduplicate(articles):
    seen = set()
    unique = []
    for a in articles:
        key = (a["title"], a["url"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique

# 主程式
all_articles = []
for source in canadian_sources:
    print(f"🔍 搜尋媒體：{source}")
    total_found = 0
    for keyword in search_keywords:
        results = fetch_articles(source, keyword)
        if results:
            print(f"  ✅ {keyword} ➜ 找到 {len(results)} 筆")
            all_articles.extend(results)
            total_found += len(results)
        else:
            print(f"  ❌ {keyword} ➜ {source} 沒資訊")
        time.sleep(2)  # 每2秒處理一個關鍵字

    if total_found == 0:
        print(f"⚠️  {source} 沒有任何資料")

# 去重、排序、儲存
final_articles = deduplicate(all_articles)
final_articles.sort(key=lambda x: x["published"], reverse=True)

news_data = {
    "source": "Google News RSS + Filtered Sources",
    "query": "Taiwan + China + Lai Ching-te + William Lai",
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "article_count": len(final_articles),
    "articles": final_articles
}

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 總共抓取 {len(final_articles)} 則新聞，已儲存到 data/news.json")

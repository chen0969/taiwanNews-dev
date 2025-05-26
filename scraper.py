import feedparser
import json
from datetime import datetime, timedelta
import time

# 媒體來源與對應網址（for site: 限定）
source_site_map = {
    "CBC": "cbc.ca",
    "Global News": "globalnews.ca",
    "CTV News": "ctvnews.ca",
    "National Post": "nationalpost.com",
    "Ottawa Citizen": "ottawacitizen.com",
    "Ottawa Sun": "ottawasun.com",
    "CityNews": "citynews.ca",
    "Hill Times": "hilltimes.com",
    "BNN Bloomberg": "bnnbloomberg.ca",
    "Canadaland": "canadaland.com",
    "iPolitics": "ipolitics.ca",
    "The Globe and Mail": "theglobeandmail.com",
    "Financial Post": "financialpost.com",
    "Maclean's": "macleans.ca",
    "The Canadian Press": "thecanadianpress.com",
    "La Presse": "lapresse.ca",
    "Vice Canada": "vice.com/en_ca",
    "The Logic": "thelogic.co",
    "The Conversation Canada": "theconversation.com/ca",
    "PressProgress": "pressprogress.ca",
    "Ottawa Matters": "ottawamatters.com",
    "Ottawa Business Journal": "obj.ca",
    "Ottawa Life Magazine": "ottawalife.com"
}

# 關鍵字（逐一查詢）
search_keywords = [
    "Taiwan",
    "China",
    "\"Lai Ching-te\"",
    "\"William Lai\""
]

# 產生 Google News RSS URL（site 限定 + 關鍵字）
def build_rss_url(site, keyword):
    keyword_encoded = keyword.replace(' ', '+')
    return f"https://news.google.com/rss/search?q={keyword_encoded}+site:{site}&hl=en-CA&gl=CA&ceid=CA:en"

# 擷取新聞資料（近 24 小時）＋過濾無關結果
def fetch_articles(source, site, keyword):
    feed = feedparser.parse(build_rss_url(site, keyword))
    now = datetime.utcnow()
    cutoff = now - timedelta(days=1)
    articles = []

    if not feed.entries:
        return []

    for entry in feed.entries:
        try:
            pub = datetime(*entry.published_parsed[:6])

            # 過濾不包含關鍵字的標題（防止誤抓）
            clean_keyword = keyword.lower().replace('"', '')
            if clean_keyword not in entry.title.lower():
                continue

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

# 去除重複（依據 title + url）
def deduplicate(articles):
    seen = set()
    unique = []
    for a in articles:
        key = (a["title"], a["url"])
        if key not in seen:
            seen.add(key)
            unique.append(a)
    return unique

# 主程式邏輯
all_articles = []
for source, site in source_site_map.items():
    print(f"🔍 搜尋媒體：{source}")
    total_found = 0
    for keyword in search_keywords:
        results = fetch_articles(source, site, keyword)
        if results:
            print(f"  ✅ {keyword} ➜ 找到 {len(results)} 筆")
            all_articles.extend(results)
            total_found += len(results)
        else:
            print(f"  ❌ {keyword} ➜ {source} 沒資訊")
        time.sleep(2)

    if total_found == 0:
        print(f"⚠️  {source} 沒有任何資料")

# 統整 + 排序 + 儲存 JSON
final_articles = deduplicate(all_articles)
final_articles.sort(key=lambda x: x["published"], reverse=True)

news_data = {
    "source": "Google News RSS + site-filtered sources",
    "query": "Taiwan + China + Lai Ching-te + William Lai",
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "article_count": len(final_articles),
    "articles": final_articles
}

# 儲存檔案
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 總共抓取 {len(final_articles)} 則新聞，已儲存到 data/news.json")

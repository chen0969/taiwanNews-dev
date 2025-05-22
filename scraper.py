import feedparser
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures

now = datetime.utcnow()
cutoff = now - timedelta(days=1)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# --- Google News RSS ---
rss_url = "https://news.google.com/rss/search?q=Taiwan&hl=en-CA&gl=CA&ceid=CA:en"
feed = feedparser.parse(rss_url)

articles = []
for entry in feed.entries:
    try:
        published_parsed = entry.published_parsed
        published_dt = datetime(*published_parsed[:6])
        if published_dt >= cutoff:
            articles.append({
                "source": "Google News",
                "title": entry.title,
                "url": entry.link,
                "published": published_dt.isoformat(),
                "date": published_dt.strftime("%Y-%m-%d")
            })
    except Exception as e:
        print("跳過無效項目:", e)
        continue

# --- 定義爬蟲函數 ---
def fetch_ctv():
    try:
        res = requests.get("https://www.ctvnews.ca/search-results/search-7.137?searchText=Taiwan", headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(".teaserTitle a")
        return [{
            "source": "CTV News",
            "title": a.get_text(strip=True),
            "url": "https://www.ctvnews.ca" + a.get("href"),
            "published": now.isoformat(),
            "date": now.strftime("%Y-%m-%d")
        } for a in items]
    except Exception as e:
        print("CTV News 失敗：", e)
        return []

def fetch_global():
    try:
        res = requests.get("https://globalnews.ca/?s=Taiwan", headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select("a.c-posts__link")
        return [{
            "source": "Global News",
            "title": a.get_text(strip=True),
            "url": a.get("href"),
            "published": now.isoformat(),
            "date": now.strftime("%Y-%m-%d")
        } for a in items]
    except Exception as e:
        print("Global News 失敗：", e)
        return []

def generic_search(name, url, selector):
    try:
        res = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.select(selector)
        return [{
            "source": name,
            "title": a.get_text(strip=True),
            "url": a.get("href") if a.get("href").startswith("http") else url.split("/search")[0] + a.get("href"),
            "published": now.isoformat(),
            "date": now.strftime("%Y-%m-%d")
        } for a in items]
    except Exception as e:
        print(f"{name} 失敗：", e)
        return []

# --- 所有網站與選擇器設定 ---
tasks = {
    "CBC News": lambda: generic_search("CBC News", "https://www.cbc.ca/search?q=Taiwan", ".card .headline a"),
    "CTV News": fetch_ctv,
    "Global News": fetch_global,
    "National Post": lambda: generic_search("National Post", "https://nationalpost.com/search/?search_text=Taiwan", "a.article-card__link"),
    "Ottawa Citizen": lambda: generic_search("Ottawa Citizen", "https://ottawacitizen.com/search/?search_text=Taiwan", "a.article-card__link"),
    "Ottawa Sun": lambda: generic_search("Ottawa Sun", "https://ottawasun.com/search/?search_text=Taiwan", "a.article-card__link"),
    "CityNews Ottawa": lambda: generic_search("CityNews Ottawa", "https://ottawa.citynews.ca/search?q=Taiwan", ".search-result a"),
    "The Hill Times": lambda: generic_search("The Hill Times", "https://www.hilltimes.com/?s=Taiwan", ".entry-title a"),
    "The Sault Star": lambda: generic_search("The Sault Star", "https://www.saultstar.com/search/?search_text=Taiwan", "a.article-card__link"),
    "The Sudbury Star": lambda: generic_search("The Sudbury Star", "https://www.thesudburystar.com/search/?search_text=Taiwan", "a.article-card__link"),
}

# --- 並行爬蟲（最多 60 秒）---
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(task): name for name, task in tasks.items()}
    try:
        for future in concurrent.futures.as_completed(futures, timeout=60):
            try:
                articles.extend(future.result())
            except Exception as exc:
                print(f"{futures[future]} 任務未完成：{exc}")
    except concurrent.futures.TimeoutError:
        print("⏰ 超過 60 秒，有些任務未完成")

# --- 儲存 JSON ---
articles.sort(key=lambda x: x["published"], reverse=True)
news_data = {
    "source": "Google News + Canadian News Sites",
    "query": "Taiwan",
    "updated_at": now.isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles
}

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"✅ 共擷取 {len(articles)} 篇文章，已儲存至 data/news.json")

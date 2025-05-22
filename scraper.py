import feedparser
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures

now = datetime.utcnow()
cutoff = now - timedelta(days=1)  # 限制 24 小時內

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

# --- CTV News 爬蟲 ---
def fetch_ctv():
    try:
        res = requests.get("https://www.ctvnews.ca/search-results/search-7.137?searchText=Taiwan", timeout=30)
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

# --- Global News 爬蟲 ---
def fetch_global():
    try:
        res = requests.get("https://globalnews.ca/?s=Taiwan", timeout=30)
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

# --- 並行執行 + timeout 控制 ---
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(fetch_ctv): "CTV",
        executor.submit(fetch_global): "Global"
    }
    for future in concurrent.futures.as_completed(futures, timeout=60):
        try:
            articles.extend(future.result())
        except Exception as exc:
            print(f"{futures[future]} 任務未完成：{exc}")

# --- 儲存 JSON ---
articles.sort(key=lambda x: x["published"], reverse=True)
news_data = {
    "source": "Google News + CTV + Global",
    "query": "Taiwan",
    "updated_at": now.isoformat() + "Z",
    "article_count": len(articles),
    "articles": articles
}

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

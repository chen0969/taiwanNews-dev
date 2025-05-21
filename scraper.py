import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_cbc_news():
    url = "https://www.cbc.ca/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch the page: {e}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    articles = []

    for item in soup.select("a.card-link"):
        title = item.get_text(strip=True)
        link = item.get("href")
        if link and not link.startswith("http"):
            link = "https://www.cbc.ca" + link
        if "taiwan" in title.lower():
            articles.append({
                "title": title,
                "url": link
            })

    print(f"[INFO] Found {len(articles)} articles about Taiwan.")
    return articles

def main():
    news = scrape_cbc_news()
    now = datetime.utcnow().isoformat()

    output = {
        "timestamp": now,
        "news": news
    }

    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")

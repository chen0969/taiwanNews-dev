import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_cbc_news():
    url = "https://www.cbc.ca/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    articles = []

    # 找新聞標題區塊（根據 CBC News 網頁結構，請依當時網站調整）
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
    main()

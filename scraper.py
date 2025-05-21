import json

# 這是假資料，實際應該從爬蟲抓的結果放進這裡
news_data = {
    "source": "Test News",
    "articles": [
        {"title": "Taiwan updates", "url": "https://example.com"},
        {"title": "More Taiwan news", "url": "https://example2.com"}
    ]
}

# 確保寫入到 data/news.json
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

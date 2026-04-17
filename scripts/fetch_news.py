"""
GitHub Actions 自动抓取新闻脚本
每 4 小时运行一次，从免费 RSS 源抓取 SpaceX/IPO 相关新闻
"""
import feedparser
import json
import re
import hashlib
import os
from datetime import datetime, timezone

RSS_FEEDS = [
    {"url": "https://feeds.reuters.com/reuters/businessNews", "source": "Reuters"},
    {"url": "https://rss.cnbc.com/rss/cnbc_tech.xml", "source": "CNBC"},
    {"url": "https://www.nasaspaceflight.com/feed/", "source": "NASASpaceFlight"},
    {"url": "https://spacenews.com/feed/", "source": "SpaceNews"},
    {"url": "https://cointelegraph.com/rss", "source": "CoinTelegraph"},
    {"url": "https://decrypt.co/feed", "source": "Decrypt"},
    {"url": "https://techcrunch.com/feed/", "source": "TechCrunch"},
]

KEYWORDS = [
    "spacex", "space x", "ipo", "starlink", "dxyz", "xovr",
    "elon musk ipo", "pre-ipo", "preipo", "starship",
    "spacex valuation", "arkx", "crypto ipo", "token ipo",
    "binance ipo", "bitget ipo", "openai ipo", "anthropic ipo",
]

CATEGORY_RULES = {
    "IPO动态":  ["ipo", "filing", "s-1", "s1", "roadshow", "listing", "sec", "valuation", "confidential", "underwriter"],
    "市场数据": ["dxyz", "xovr", "arkx", "nav", "premium", "discount", "token", "price", "trading"],
    "成份股":   ["starlink", "satellite", "starship", "launch", "falcon", "reentry", "booster"],
}

def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()

def make_id(url, title):
    return hashlib.md5(f"{url}|{title}".encode()).hexdigest()[:12]

def matches(text):
    t = text.lower()
    return any(kw in t for kw in KEYWORDS)

def categorize(text):
    t = text.lower()
    for cat, terms in CATEGORY_RULES.items():
        if any(term in t for term in terms):
            return cat
    return "IPO动态"

def to_iso(parsed_time):
    if parsed_time:
        try:
            dt = datetime(*parsed_time[:6], tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def fetch_all():
    items = []
    for feed_info in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:25]:
                title   = strip_html(entry.get("title", ""))
                summary = strip_html(entry.get("summary") or entry.get("description", ""))[:250]
                link    = entry.get("link", "")

                if not matches(title + " " + summary):
                    continue

                items.append({
                    "id":         make_id(link, title),
                    "time":       to_iso(entry.get("published_parsed") or entry.get("updated_parsed")),
                    "title":      title,
                    "summary":    summary,
                    "source":     feed_info["source"],
                    "source_url": link,
                    "category":   categorize(title + " " + summary),
                    "pinned":     False,
                })
        except Exception as e:
            print(f"[WARN] Failed to fetch {feed_info['url']}: {e}")

    # 去重
    seen = set()
    unique = []
    for item in items:
        if item["id"] not in seen:
            seen.add(item["id"])
            unique.append(item)

    # 按时间倒序
    unique.sort(key=lambda x: x["time"], reverse=True)

    # 加载现有数据，保留置顶
    news_path = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
    existing_pinned = []
    if os.path.exists(news_path):
        with open(news_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing_pinned = [i for i in existing if i.get("pinned")]
        pinned_ids = {i["id"] for i in existing_pinned}
        unique = [i for i in unique if i["id"] not in pinned_ids]

    final = existing_pinned + unique
    final = final[:40]  # 最多保留 40 条

    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"[OK] news.json updated: {len(final)} items ({len(existing_pinned)} pinned + {len(unique)} fetched)")

if __name__ == "__main__":
    fetch_all()

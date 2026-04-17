"""
GitHub Actions 自动抓取新闻脚本（中英双语）
每 4 小时运行一次
"""
import feedparser
import json
import re
import hashlib
import os
from datetime import datetime, timezone

# 中文优先 RSS 源
RSS_FEEDS = [
    {"url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",    "source": "BBC中文", "lang": "zh"},
    {"url": "https://rss.cnn.com/rss/edition_china.rss",          "source": "CNN中文", "lang": "zh"},
    {"url": "https://www.nasaspaceflight.com/feed/",              "source": "NASASpaceFlight", "lang": "en"},
    {"url": "https://spacenews.com/feed/",                        "source": "SpaceNews", "lang": "en"},
    {"url": "https://feeds.reuters.com/reuters/businessNews",     "source": "路透社", "lang": "en"},
    {"url": "https://cointelegraph.com/rss",                      "source": "CoinTelegraph", "lang": "en"},
    {"url": "https://decrypt.co/feed",                            "source": "Decrypt", "lang": "en"},
    {"url": "https://techcrunch.com/feed/",                       "source": "TechCrunch", "lang": "en"},
]

KEYWORDS = [
    "spacex", "space x", "ipo", "starlink", "dxyz", "xovr",
    "starship", "elon musk", "pre-ipo", "preipo",
    "openai", "anthropic", "valuation", "sec filing",
    "arkx", "crypto ipo", "token", "binance ipo", "bitget",
    "上市", "估值", "路演", "申报", "承销",
]

CATEGORY_RULES = {
    "IPO动态": ["ipo", "filing", "s-1", "roadshow", "listing", "sec", "valuation", "上市", "申报", "路演", "承销"],
    "市场数据": ["dxyz", "xovr", "arkx", "nav", "premium", "token", "price", "溢价", "交易"],
    "成份股":   ["starlink", "starship", "launch", "falcon", "satellite", "星舰", "发射", "卫星"],
}

# 简单的英→中 摘要映射（关键词替换）
SOURCE_CN_MAP = {
    "Reuters": "路透社", "CNBC": "CNBC", "TechCrunch": "TechCrunch",
    "NASASpaceFlight": "NASASpaceFlight", "SpaceNews": "SpaceNews",
    "CoinTelegraph": "CoinTelegraph", "Decrypt": "Decrypt",
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
            for entry in feed.entries[:20]:
                title   = strip_html(entry.get("title", ""))
                summary = strip_html(entry.get("summary") or entry.get("description", ""))[:280]
                link    = entry.get("link", "")

                if not matches(title + " " + summary):
                    continue

                source_name = SOURCE_CN_MAP.get(feed_info["source"], feed_info["source"])

                items.append({
                    "id":         make_id(link, title),
                    "time":       to_iso(entry.get("published_parsed") or entry.get("updated_parsed")),
                    "title":      title,
                    "summary":    summary,
                    "source":     source_name,
                    "source_url": link,
                    "category":   categorize(title + " " + summary),
                    "pinned":     False,
                })
        except Exception as e:
            print(f"[WARN] {feed_info['url']}: {e}")

    # 去重 + 排序
    seen, unique = set(), []
    for item in items:
        if item["id"] not in seen:
            seen.add(item["id"])
            unique.append(item)
    unique.sort(key=lambda x: x["time"], reverse=True)

    # 保留置顶
    news_path = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
    existing_pinned = []
    if os.path.exists(news_path):
        with open(news_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing_pinned = [i for i in existing if i.get("pinned")]
        pinned_ids = {i["id"] for i in existing_pinned}
        unique = [i for i in unique if i["id"] not in pinned_ids]

    final = existing_pinned + unique
    final = final[:40]

    with open(news_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(final)} items ({len(existing_pinned)} pinned + {len(unique)} new)")

if __name__ == "__main__":
    fetch_all()

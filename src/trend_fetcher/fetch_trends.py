"""Fetch trends from public sources and store normalized results."""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

try:
    from pytrends.request import TrendReq
except ImportError:  # Google Trends is an optional source.
    TrendReq = None

USER_AGENT = "AI-Solopreneur-Bot/1.0 (Educational/Research)"
REQUEST_DELAY = 2
REQUEST_TIMEOUT = 10
REDDIT_SUBREDDITS = [
    "Entrepreneur", "SideHustle", "Productivity", "ArtificialIntelligence",
    "solopreneur", "passive_income", "digitalnomad",
]
NICHE_KEYWORDS = [
    "AI", "artificial intelligence", "machine learning", "automation", "automate",
    "solopreneur", "entrepreneur", "freelancer", "freelance", "online business",
    "side hustle", "passive income", "digital products", "productivity", "efficiency",
    "tools", "workflow", "money", "revenue", "profit", "income", "earn",
]


def _get_json(url: str, *, headers: Optional[dict] = None):
    """Fetch JSON and reject HTTP and malformed-response errors consistently."""
    response = requests.get(
        url, headers=headers or {"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def fetch_reddit_trends(max_per_subreddit: int = 10) -> List[Dict]:
    trends = []
    headers = {"User-Agent": USER_AGENT}
    print(f"📱 Fetching from Reddit ({len(REDDIT_SUBREDDITS)} subreddits)...")
    for subreddit in REDDIT_SUBREDDITS:
        try:
            data = _get_json(
                f"https://www.reddit.com/r/{subreddit}/hot.json?limit={max(1, max_per_subreddit)}",
                headers=headers,
            )
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                post_data = post.get("data", {})
                topic = (post_data.get("title") or "").strip()
                if topic:
                    trends.append({
                        "topic": topic,
                        "source": f"reddit-{subreddit}",
                        "score": max(0, post_data.get("score", 0)) + max(0, post_data.get("num_comments", 0)),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "timestamp": datetime.now(),
                        "keywords": extract_keywords(topic),
                    })
            print(f"  ✓ r/{subreddit}: {len(posts)} posts")
        except (requests.RequestException, ValueError, TypeError, AttributeError) as exc:
            print(f"  ✗ r/{subreddit}: {exc}")
        time.sleep(REQUEST_DELAY)
    return trends


def fetch_hackernews_trends(max_stories: int = 30) -> List[Dict]:
    trends = []
    print("🔶 Fetching from Hacker News...")
    try:
        story_ids = _get_json("https://hacker-news.firebaseio.com/v0/topstories.json")
        if not isinstance(story_ids, list):
            raise ValueError("Unexpected Hacker News top stories response")
    except (requests.RequestException, ValueError, TypeError) as exc:
        print(f"  ✗ Hacker News: {exc}")
        return trends

    for story_id in story_ids[:max(0, max_stories)]:
        try:
            story = _get_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
            if not isinstance(story, dict) or not story.get("title"):
                continue
            title = story["title"].strip()
            trends.append({
                "topic": title,
                "source": "hackernews",
                "score": max(0, story.get("score", 0)) + max(0, story.get("descendants", 0)),
                "url": story.get("url") or f"https://news.ycombinator.com/item?id={story_id}",
                "timestamp": datetime.now(),
                "keywords": extract_keywords(title),
            })
        except (requests.RequestException, ValueError, TypeError, AttributeError) as exc:
            print(f"  ✗ HN story {story_id}: {exc}")
        time.sleep(0.5)
    print(f"  ✓ Fetched {len(trends)} stories")
    return trends


def fetch_google_trends(keywords: Optional[List[str]] = None) -> List[Dict]:
    if TrendReq is None:
        print("⚠️ pytrends is not installed; skipping Google Trends")
        return []
    trends = []
    keywords = keywords or ["AI", "solopreneur", "productivity", "side hustle", "automation"]
    print("🔍 Fetching from Google Trends...")
    try:
        pytrend = TrendReq(hl="en-US", tz=360)
    except Exception as exc:
        print(f"  ✗ Could not initialize Google Trends: {exc}")
        return trends

    for keyword in keywords:
        try:
            pytrend.build_payload([keyword], timeframe="now 7-d")
            related = pytrend.related_queries() or {}
            entry = related.get(keyword) or {}
            top_queries = entry.get("top")
            if top_queries is not None:
                for _, row in top_queries.head(5).iterrows():
                    query = str(row.get("query", "")).strip()
                    if not query:
                        continue
                    trends.append({
                        "topic": query,
                        "source": "google-trends",
                        "score": max(0, int(row.get("value", 0))),
                        "url": f"https://trends.google.com/trends/explore?q={quote(keyword)}",
                        "timestamp": datetime.now(),
                        "keywords": extract_keywords(query),
                    })
        except Exception as exc:
            print(f"  ✗ Google Trends {keyword}: {exc}")
        time.sleep(REQUEST_DELAY)
    print(f"  ✓ Fetched {len(trends)} trends")
    return trends


def _parse_star_count(text: str) -> int:
    """Parse counts such as '1,234 stars today'; return zero if unavailable."""
    for token in text.replace(",", "").split():
        if token.isdigit():
            return int(token)
    return 0


def fetch_github_trending() -> List[Dict]:
    """Fetch repositories from GitHub Trending, tolerating markup variations."""
    trends = []
    print("🐙 Fetching from GitHub Trending...")
    try:
        response = requests.get(
            "https://github.com/trending", headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # GitHub has changed these classes more than once; use article rows if present,
        # then fall back to repository links so a CSS class rename doesn't break fetches.
        repos = soup.select("article")
        if not repos:
            repos = [link.parent.parent for link in soup.select('a[href^="/"][itemprop="url"]') if link.parent and link.parent.parent]
        seen = set()
        for repo in repos:
            link = repo.select_one('h2 a[href], a[itemprop="url"][href]')
            if not link:
                continue
            path = link.get("href", "").strip("/")
            if path.count("/") != 1 or path in seen:
                continue
            seen.add(path)
            description_node = repo.select_one("p")
            description = description_node.get_text(" ", strip=True) if description_node else path
            star_node = repo.select_one('a[href$="/stargazers"]')
            stars = _parse_star_count(star_node.parent.get_text(" ", strip=True)) if star_node and star_node.parent else 0
            trends.append({
                "topic": description or path,
                "source": "github",
                "score": stars,
                "url": f"https://github.com/{path}",
                "timestamp": datetime.now(),
                "keywords": extract_keywords(description or path),
            })
            if len(trends) >= 20:
                break
        if not trends:
            print("  ⚠️ GitHub Trending page structure was not recognized; skipping source")
        else:
            print(f"  ✓ Fetched {len(trends)} repositories")
    except (requests.RequestException, ValueError, AttributeError) as exc:
        print(f"  ✗ GitHub Trending: {exc}")
    return trends


def extract_keywords(text: str) -> List[str]:
    text_lower = (text or "").lower()
    return [keyword for keyword in NICHE_KEYWORDS if keyword.lower() in text_lower]


def normalize_trends(raw_trends: List[Dict]) -> List[Dict]:
    normalized = []
    for trend in raw_trends or []:
        if not isinstance(trend, dict):
            continue
        topic = str(trend.get("topic") or "").strip()
        if not topic:
            continue
        try:
            score = max(0, int(trend.get("score") or 0))
        except (TypeError, ValueError):
            score = 0
        keywords = trend.get("keywords") or []
        normalized.append({
            "topic": topic,
            "source": str(trend.get("source") or "unknown"),
            "score": score,
            "url": str(trend.get("url") or ""),
            "timestamp": trend.get("timestamp") or datetime.now(),
            "keywords": [str(item) for item in keywords] if isinstance(keywords, (list, tuple)) else [],
        })
    return normalized


def store_trends_to_sqlite(trends: List[Dict], db_path: str = "data/solopreneur.db") -> int:
    import sqlite3

    parent = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(parent, exist_ok=True)
    stored_count = 0
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT NOT NULL, source TEXT,
                score INTEGER, url TEXT, keywords TEXT, hashtags TEXT,
                engagement_score INTEGER, tweet_count INTEGER, category TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for trend in normalize_trends(trends):
            try:
                cursor.execute(
                    "INSERT INTO trends (topic, source, score, url, keywords, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (trend["topic"], trend["source"], trend["score"], trend["url"], json.dumps(trend["keywords"]), trend["timestamp"]),
                )
                stored_count += 1
            except sqlite3.Error as exc:
                print(f"⚠️ Failed to store trend {trend['topic']!r}: {exc}")
    print(f"\n💾 Stored {stored_count} trends to database")
    return stored_count


def get_raw_trends_from_source() -> List[Dict]:
    """Fetch from every source independently so one outage doesn't stop the run."""
    all_trends = []
    print("🔍 Fetching trends from multiple sources...\n")
    for source_name, fetcher in (
        ("Reddit", fetch_reddit_trends),
        ("Hacker News", fetch_hackernews_trends),
        ("Google Trends", fetch_google_trends),
        ("GitHub", fetch_github_trending),
    ):
        try:
            all_trends.extend(fetcher())
        except Exception as exc:
            print(f"⚠️ {source_name} source failed unexpectedly: {exc}")
    print(f"\n📊 Total raw trends fetched: {len(all_trends)}")
    return all_trends


if __name__ == "__main__":
    normalized = normalize_trends(get_raw_trends_from_source())
    print(f"\n✅ Normalized {len(normalized)} trends")
    for trend in normalized[:5]:
        print(f"  - [{trend['source']}] {trend['topic'][:80]}... (score: {trend['score']})")

"""
Trend Fetcher Module

Fetches trending topics from multiple free, public sources:
- Reddit (public API)
- Hacker News (public API)
- Google Trends (pytrends)
- GitHub Trending (web scraping)
"""

import requests
import time
import json
from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
import sqlite3
import os

# Try to import pytrends (optional)
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️  pytrends not installed. Google Trends will be skipped.")


# Configuration
USER_AGENT = "AI-Solopreneur-Bot/1.0 (Educational/Research)"
REQUEST_DELAY = 2  # seconds between requests

REDDIT_SUBREDDITS = [
    "Entrepreneur",
    "SideHustle",
    "Productivity",
    "ArtificialIntelligence",
    "solopreneur",
    "passive_income",
    "digitalnomad"
]

NICHE_KEYWORDS = [
    "AI", "artificial intelligence", "machine learning", "automation", "automate",
    "solopreneur", "entrepreneur", "freelancer", "freelance",
    "online business", "side hustle", "passive income", "digital products",
    "productivity", "efficiency", "tools", "workflow",
    "money", "revenue", "profit", "income", "earn"
]


def fetch_reddit_trends(max_per_subreddit: int = 10) -> List[Dict]:
    """
    Fetch trending posts from Reddit using public API (no auth required).
    
    Args:
        max_per_subreddit: Maximum posts to fetch per subreddit
        
    Returns:
        List of trend dictionaries
    """
    trends = []
    headers = {'User-Agent': USER_AGENT}
    
    print(f"📱 Fetching from Reddit ({len(REDDIT_SUBREDDITS)} subreddits)...")
    
    for subreddit in REDDIT_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={max_per_subreddit}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                for post in posts:
                    post_data = post.get('data', {})
                    
                    trend = {
                        'topic': post_data.get('title', ''),
                        'source': f'reddit-{subreddit}',
                        'score': post_data.get('score', 0) + post_data.get('num_comments', 0),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'timestamp': datetime.now(),
                        'keywords': extract_keywords(post_data.get('title', ''))
                    }
                    
                    if trend['topic']:
                        trends.append(trend)
                
                print(f"  ✓ r/{subreddit}: {len(posts)} posts")
            else:
                print(f"  ✗ r/{subreddit}: HTTP {response.status_code}")
            
            time.sleep(REQUEST_DELAY)  # Rate limiting
            
        except Exception as e:
            print(f"  ✗ r/{subreddit}: {str(e)}")
            continue
    
    return trends


def fetch_hackernews_trends(max_stories: int = 30) -> List[Dict]:
    """
    Fetch trending stories from Hacker News API.
    
    Args:
        max_stories: Maximum stories to fetch
        
    Returns:
        List of trend dictionaries
    """
    trends = []
    
    print(f"🔶 Fetching from Hacker News...")
    
    try:
        # Get top story IDs
        response = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            timeout=10
        )
        
        if response.status_code == 200:
            story_ids = response.json()[:max_stories]
            
            # Fetch each story
            for story_id in story_ids:
                try:
                    story_response = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                        timeout=10
                    )
                    
                    if story_response.status_code == 200:
                        story = story_response.json()
                        
                        if story and story.get('title'):
                            trend = {
                                'topic': story.get('title', ''),
                                'source': 'hackernews',
                                'score': story.get('score', 0) + story.get('descendants', 0),
                                'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                'timestamp': datetime.now(),
                                'keywords': extract_keywords(story.get('title', ''))
                            }
                            trends.append(trend)
                    
                    time.sleep(0.5)  # Small delay between story fetches
                    
                except Exception as e:
                    continue
            
            print(f"  ✓ Fetched {len(trends)} stories")
        else:
            print(f"  ✗ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    return trends


def fetch_google_trends(keywords: List[str] = None) -> List[Dict]:
    """
    Fetch trending topics from Google Trends using pytrends.
    
    Args:
        keywords: List of keywords to check trends for
        
    Returns:
        List of trend dictionaries
    """
    if not PYTRENDS_AVAILABLE:
        return []
    
    trends = []
    
    if keywords is None:
        keywords = ["AI", "solopreneur", "productivity", "side hustle", "automation"]
    
    print(f"🔍 Fetching from Google Trends...")
    
    try:
        pytrend = TrendReq(hl='en-US', tz=360)
        
        for keyword in keywords:
            try:
                # Build payload
                pytrend.build_payload([keyword], timeframe='now 7-d')
                
                # Get related queries
                related = pytrend.related_queries()
                
                if keyword in related and related[keyword]['top'] is not None:
                    top_queries = related[keyword]['top']
                    
                    for _, row in top_queries.head(5).iterrows():
                        trend = {
                            'topic': row['query'],
                            'source': 'google-trends',
                            'score': int(row['value']),
                            'url': f"https://trends.google.com/trends/explore?q={keyword}",
                            'timestamp': datetime.now(),
                            'keywords': extract_keywords(row['query'])
                        }
                        trends.append(trend)
                
                time.sleep(REQUEST_DELAY)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ {keyword}: {str(e)}")
                continue
        
        print(f"  ✓ Fetched {len(trends)} trends")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    return trends


def fetch_github_trending() -> List[Dict]:
    """
    Fetch trending repositories from GitHub (web scraping).
    
    Returns:
        List of trend dictionaries
    """
    trends = []
    
    print(f"🐙 Fetching from GitHub Trending...")
    
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(
            "https://github.com/trending",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            repos = soup.find_all('article', class_='Box-row')
            
            for repo in repos[:20]:  # Top 20
                try:
                    # Get repo name
                    h2 = repo.find('h2')
                    if h2:
                        repo_name = h2.get_text().strip().replace('\n', '').replace(' ', '')
                        
                        # Get description
                        desc = repo.find('p', class_='col-9')
                        description = desc.get_text().strip() if desc else repo_name
                        
                        # Get stars today
                        stars_span = repo.find('span', class_='d-inline-block float-sm-right')
                        stars = 0
                        if stars_span:
                            stars_text = stars_span.get_text().strip()
                            try:
                                stars = int(stars_text.split()[0].replace(',', ''))
                            except:
                                stars = 100  # Default
                        
                        trend = {
                            'topic': description,
                            'source': 'github',
                            'score': stars,
                            'url': f"https://github.com/{repo_name}",
                            'timestamp': datetime.now(),
                            'keywords': extract_keywords(description)
                        }
                        trends.append(trend)
                        
                except Exception as e:
                    continue
            
            print(f"  ✓ Fetched {len(trends)} repositories")
        else:
            print(f"  ✗ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    return trends


def extract_keywords(text: str) -> List[str]:
    """
    Extract matching keywords from text.
    
    Args:
        text: Text to extract keywords from
        
    Returns:
        List of matched keywords
    """
    text_lower = text.lower()
    matched = []
    
    for keyword in NICHE_KEYWORDS:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return matched


def normalize_trends(raw_trends: List[Dict]) -> List[Dict]:
    """
    Normalize trends from different sources to consistent format.
    
    Args:
        raw_trends: Raw trends from various sources
        
    Returns:
        Normalized trends
    """
    normalized = []
    
    for trend in raw_trends:
        # Ensure all required fields exist
        normalized_trend = {
            'topic': trend.get('topic', '').strip(),
            'source': trend.get('source', 'unknown'),
            'score': max(0, trend.get('score', 0)),
            'url': trend.get('url', ''),
            'timestamp': trend.get('timestamp', datetime.now()),
            'keywords': trend.get('keywords', [])
        }
        
        # Only include if topic is not empty
        if normalized_trend['topic']:
            normalized.append(normalized_trend)
    
    return normalized


def store_trends_to_sqlite(trends: List[Dict], db_path: str = "data/solopreneur.db"):
    """
    Store trends in SQLite database.
    
    Args:
        trends: List of normalized trends
        db_path: Path to SQLite database
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stored_count = 0
    
    for trend in trends:
        try:
            cursor.execute("""
                INSERT INTO trends (topic, source, score, url, keywords, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                trend['topic'],
                trend['source'],
                trend['score'],
                trend['url'],
                json.dumps(trend['keywords']),
                trend['timestamp']
            ))
            stored_count += 1
        except Exception as e:
            # Skip duplicates or errors
            continue
    
    conn.commit()
    conn.close()
    
    print(f"\n💾 Stored {stored_count} trends to database")
    return stored_count


def get_raw_trends_from_source() -> List[Dict]:
    """
    Main function to fetch trends from all sources.
    
    Returns:
        Combined list of raw trends
    """
    all_trends = []
    
    print("🔍 Fetching trends from multiple sources...\n")
    
    # Fetch from Reddit
    reddit_trends = fetch_reddit_trends(max_per_subreddit=10)
    all_trends.extend(reddit_trends)
    
    # Fetch from Hacker News
    hn_trends = fetch_hackernews_trends(max_stories=30)
    all_trends.extend(hn_trends)
    
    # Fetch from Google Trends
    google_trends = fetch_google_trends()
    all_trends.extend(google_trends)
    
    # Fetch from GitHub
    github_trends = fetch_github_trending()
    all_trends.extend(github_trends)
    
    print(f"\n📊 Total raw trends fetched: {len(all_trends)}")
    
    return all_trends


if __name__ == "__main__":
    # Test the fetcher
    trends = get_raw_trends_from_source()
    normalized = normalize_trends(trends)
    
    print(f"\n✅ Normalized {len(normalized)} trends")
    print("\nSample trends:")
    for trend in normalized[:5]:
        print(f"  - [{trend['source']}] {trend['topic'][:80]}... (score: {trend['score']})")

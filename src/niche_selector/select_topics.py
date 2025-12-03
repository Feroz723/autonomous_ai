"""
Niche Selector Module

Loads recent trends, filters by niche keywords, and ranks topics
based on engagement, relevance, and recency.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter


# Niche keywords with weights
NICHE_KEYWORDS = {
    # AI & Tech
    "AI": 3,
    "artificial intelligence": 3,
    "machine learning": 2,
    "automation": 3,
    "automate": 2,
    "ChatGPT": 2,
    "GPT": 2,
    
    # Business
    "solopreneur": 5,
    "entrepreneur": 4,
    "freelancer": 4,
    "freelance": 3,
    "startup": 2,
    
    # Income
    "online business": 5,
    "side hustle": 5,
    "passive income": 4,
    "digital products": 4,
    "money": 2,
    "revenue": 2,
    "profit": 2,
    "income": 3,
    "earn": 2,
    
    # Productivity
    "productivity": 4,
    "efficiency": 3,
    "tools": 2,
    "workflow": 2,
    "remote work": 3,
    
    # Marketing
    "marketing": 2,
    "social media": 2,
    "content": 2,
    "SEO": 2,
}


def load_recent_trends(db_path: str = "data/solopreneur.db", hours: int = 24) -> List[Dict]:
    """
    Load trends from the database that were fetched within the last N hours.
    
    Args:
        db_path: Path to SQLite database
        hours: Number of hours to look back
        
    Returns:
        List of trend dictionaries
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Calculate cutoff time
    cutoff = datetime.now() - timedelta(hours=hours)
    
    cursor.execute("""
        SELECT id, topic, source, score, url, keywords, fetched_at
        FROM trends
        WHERE fetched_at >= ?
        ORDER BY fetched_at DESC
    """, (cutoff,))
    
    rows = cursor.fetchall()
    conn.close()
    
    trends = []
    for row in rows:
        trend = {
            'id': row[0],
            'topic': row[1],
            'source': row[2],
            'score': row[3],
            'url': row[4],
            'keywords': json.loads(row[5]) if row[5] else [],
            'fetched_at': datetime.fromisoformat(row[6]) if isinstance(row[6], str) else row[6]
        }
        trends.append(trend)
    
    return trends


def filter_by_niche(trends: List[Dict], min_keyword_matches: int = 1) -> List[Dict]:
    """
    Filter trends that match niche keywords.
    
    Args:
        trends: List of trends to filter
        min_keyword_matches: Minimum number of keyword matches required
        
    Returns:
        Filtered list of trends
    """
    filtered = []
    
    for trend in trends:
        # Count keyword matches
        keyword_matches = len(trend.get('keywords', []))
        
        # Also check topic text for keywords
        topic_lower = trend['topic'].lower()
        additional_matches = 0
        
        for keyword in NICHE_KEYWORDS.keys():
            if keyword.lower() in topic_lower and keyword not in trend.get('keywords', []):
                additional_matches += 1
        
        total_matches = keyword_matches + additional_matches
        
        if total_matches >= min_keyword_matches:
            trend['keyword_match_count'] = total_matches
            filtered.append(trend)
    
    return filtered


def calculate_relevance_score(trend: Dict) -> float:
    """
    Calculate relevance score based on keyword matches and weights.
    
    Args:
        trend: Trend dictionary
        
    Returns:
        Relevance score (0-100)
    """
    topic_lower = trend['topic'].lower()
    total_weight = 0
    
    for keyword, weight in NICHE_KEYWORDS.items():
        if keyword.lower() in topic_lower:
            total_weight += weight
    
    # Normalize to 0-100 scale
    max_possible_weight = 20  # Approximate max
    relevance = min(100, (total_weight / max_possible_weight) * 100)
    
    return relevance


def calculate_recency_factor(trend: Dict) -> float:
    """
    Calculate recency factor (newer = higher score).
    
    Args:
        trend: Trend dictionary
        
    Returns:
        Recency factor (0-100)
    """
    now = datetime.now()
    fetched_at = trend.get('fetched_at', now)
    
    if isinstance(fetched_at, str):
        fetched_at = datetime.fromisoformat(fetched_at)
    
    hours_ago = (now - fetched_at).total_seconds() / 3600
    
    # Decay over 24 hours
    if hours_ago <= 1:
        return 100
    elif hours_ago <= 6:
        return 80
    elif hours_ago <= 12:
        return 60
    elif hours_ago <= 24:
        return 40
    else:
        return 20


def rank_topics(trends: List[Dict]) -> List[Dict]:
    """
    Rank topics by engagement, relevance, and recency.
    
    Ranking formula:
        score = 0.5 * normalized_engagement + 0.3 * relevance + 0.2 * recency
    
    Args:
        trends: List of trends to rank
        
    Returns:
        Sorted list of trends with ranking scores
    """
    if not trends:
        return []
    
    # Find max score for normalization
    max_engagement = max(trend.get('score', 0) for trend in trends)
    max_engagement = max(max_engagement, 1)  # Avoid division by zero
    
    ranked = []
    
    for trend in trends:
        # Normalize engagement score (0-100)
        normalized_engagement = (trend.get('score', 0) / max_engagement) * 100
        
        # Calculate relevance
        relevance = calculate_relevance_score(trend)
        
        # Calculate recency
        recency = calculate_recency_factor(trend)
        
        # Calculate final score
        final_score = (
            0.5 * normalized_engagement +
            0.3 * relevance +
            0.2 * recency
        )
        
        trend['engagement_normalized'] = round(normalized_engagement, 2)
        trend['relevance_score'] = round(relevance, 2)
        trend['recency_factor'] = round(recency, 2)
        trend['final_score'] = round(final_score, 2)
        
        ranked.append(trend)
    
    # Sort by final score (descending)
    ranked.sort(key=lambda x: x['final_score'], reverse=True)
    
    return ranked


def get_top_keywords(trends: List[Dict], top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Get most common keywords from trends.
    
    Args:
        trends: List of trends
        top_n: Number of top keywords to return
        
    Returns:
        List of (keyword, count) tuples
    """
    all_keywords = []
    
    for trend in trends:
        all_keywords.extend(trend.get('keywords', []))
    
    keyword_counts = Counter(all_keywords)
    return keyword_counts.most_common(top_n)


def select_topics(
    db_path: str = "data/solopreneur.db",
    hours: int = 24,
    min_keyword_matches: int = 1,
    top_n: int = 10
) -> List[Dict]:
    """
    Main function to select top topics from recent trends.
    
    Args:
        db_path: Path to SQLite database
        hours: Hours to look back
        min_keyword_matches: Minimum keyword matches required
        top_n: Number of top topics to return
        
    Returns:
        List of top-ranked topics
    """
    # Load recent trends
    trends = load_recent_trends(db_path, hours)
    print(f"📊 Loaded {len(trends)} recent trends (last {hours}h)")
    
    if not trends:
        print("⚠️  No recent trends found. Run trend fetcher first.")
        return []
    
    # Filter by niche
    filtered = filter_by_niche(trends, min_keyword_matches)
    print(f"🎯 Filtered to {len(filtered)} niche-relevant trends")
    
    if not filtered:
        print("⚠️  No trends matched niche keywords.")
        return []
    
    # Rank topics
    ranked = rank_topics(filtered)
    
    # Get top N
    top_topics = ranked[:top_n]
    
    return top_topics


def print_top_topics(topics: List[Dict], show_details: bool = True):
    """
    Pretty print top topics.
    
    Args:
        topics: List of ranked topics
        show_details: Whether to show detailed scores
    """
    if not topics:
        print("No topics to display.")
        return
    
    print(f"\n🏆 Top {len(topics)} Selected Topics:\n")
    
    for i, topic in enumerate(topics, 1):
        print(f"{i}. [Score: {topic['final_score']}] {topic['topic'][:80]}")
        
        if show_details:
            print(f"   Source: {topic['source']} | Engagement: {topic['score']} | "
                  f"Relevance: {topic['relevance_score']} | Recency: {topic['recency_factor']}")
            print(f"   Keywords: {', '.join(topic.get('keywords', [])[:5])}")
            print(f"   URL: {topic['url']}")
        
        print()


if __name__ == "__main__":
    # Test the selector
    top_topics = select_topics(top_n=10)
    print_top_topics(top_topics, show_details=True)
    
    # Show top keywords
    if top_topics:
        print("\n📌 Most Common Keywords:")
        top_keywords = get_top_keywords(top_topics, top_n=10)
        for keyword, count in top_keywords:
            print(f"  - {keyword}: {count}")

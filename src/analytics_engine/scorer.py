"""
Analytics Scorer

Calculates topic-level performance scores and recommendations.
"""

import sqlite3
from typing import Dict, List
from collections import defaultdict
from .models import PerformanceRecord, TopicPerformance

# Keywords to identify topics from tweet text
TOPIC_KEYWORDS = {
    'AI': ['ai', 'artificial intelligence', 'machine learning', 'gpt', 'chatgpt'],
    'Automation': ['automation', 'automate', 'workflow', 'zapier'],
    'Productivity': ['productivity', 'productive', 'efficiency', 'time management'],
    'Solopreneur': ['solopreneur', 'solo', 'indie hacker', 'founder'],
    'Side Hustle': ['side hustle', 'passive income', 'extra income'],
    'Content': ['content', 'writing', 'blog', 'newsletter'],
    'Marketing': ['marketing', 'growth', 'seo', 'traffic']
}

def identify_topic(tweet_text: str) -> str:
    """Identify topic from tweet text using keywords."""
    tweet_lower = tweet_text.lower()
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in tweet_lower:
                return topic
    
    return "General"

def load_performance_records(db_path: str) -> List[PerformanceRecord]:
    """Load all performance records from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tweet_performance")
    rows = cursor.fetchall()
    
    records = []
    for row in rows:
        record = PerformanceRecord(
            tweet_id=row[0],
            tweet_text=row[1],
            topic=row[2] or identify_topic(row[1]),
            impressions=row[3],
            likes=row[4],
            reposts=row[5],
            bookmarks=row[6],
            replies=row[7],
            engagement_score=row[8],
            created_at=row[9]
        )
        records.append(record)
    
    conn.close()
    return records

def calculate_topic_scores(records: List[PerformanceRecord]) -> Dict[str, TopicPerformance]:
    """Calculate aggregated scores per topic."""
    topic_data = defaultdict(lambda: {
        'tweets': [],
        'total_impressions': 0,
        'total_engagement': 0.0,
        'total_likes': 0,
        'total_reposts': 0
    })
    
    # Aggregate data
    for record in records:
        topic = record.topic or identify_topic(record.tweet_text)
        topic_data[topic]['tweets'].append(record)
        topic_data[topic]['total_impressions'] += record.impressions
        topic_data[topic]['total_engagement'] += record.engagement_score
        topic_data[topic]['total_likes'] += record.likes
        topic_data[topic]['total_reposts'] += record.reposts
    
    # Calculate averages
    topic_scores = {}
    
    for topic, data in topic_data.items():
        tweets = data['tweets']
        count = len(tweets)
        
        if count == 0:
            continue
        
        # Find best and worst tweets
        sorted_tweets = sorted(tweets, key=lambda x: x.engagement_score, reverse=True)
        
        topic_perf = TopicPerformance(
            topic=topic,
            total_tweets=count,
            avg_impressions=data['total_impressions'] / count,
            avg_engagement_score=data['total_engagement'] / count,
            total_likes=data['total_likes'],
            total_reposts=data['total_reposts'],
            best_tweet_id=sorted_tweets[0].tweet_id if sorted_tweets else None,
            worst_tweet_id=sorted_tweets[-1].tweet_id if sorted_tweets else None
        )
        
        topic_scores[topic] = topic_perf
    
    return topic_scores

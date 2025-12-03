"""
Analytics CSV Importer

Imports Twitter/X analytics from CSV exports.
"""

import csv
import sqlite3
from typing import List
from datetime import datetime
from .models import PerformanceRecord

def import_analytics_csv(csv_path: str) -> List[PerformanceRecord]:
    """
    Import analytics from Twitter CSV export.
    
    Expected columns:
    - Tweet id
    - Tweet text
    - impressions
    - likes
    - retweets
    - bookmarks
    - replies (optional)
    - created_at
    """
    records = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Handle different column name variations
            tweet_id = row.get('Tweet id', row.get('tweet_id', ''))
            tweet_text = row.get('Tweet text', row.get('tweet_text', ''))
            
            record = PerformanceRecord(
                tweet_id=str(tweet_id),
                tweet_text=tweet_text,
                impressions=int(row.get('impressions', 0)),
                likes=int(row.get('likes', 0)),
                reposts=int(row.get('retweets', row.get('reposts', 0))),
                bookmarks=int(row.get('bookmarks', 0)),
                replies=int(row.get('replies', 0)),
                created_at=row.get('created_at', row.get('time', ''))
            )
            
            # Calculate engagement score
            record.engagement_score = record.calculate_engagement_score()
            
            records.append(record)
    
    return records

def save_to_analytics_db(records: List[PerformanceRecord], db_path: str):
    """Save performance records to analytics database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweet_performance (
            tweet_id TEXT PRIMARY KEY,
            tweet_text TEXT,
            topic TEXT,
            impressions INTEGER,
            likes INTEGER,
            reposts INTEGER,
            bookmarks INTEGER,
            replies INTEGER,
            engagement_score REAL,
            created_at TEXT
        )
    """)
    
    # Insert records
    for record in records:
        cursor.execute("""
            INSERT OR REPLACE INTO tweet_performance 
            (tweet_id, tweet_text, topic, impressions, likes, reposts, bookmarks, replies, engagement_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.tweet_id,
            record.tweet_text,
            record.topic,
            record.impressions,
            record.likes,
            record.reposts,
            record.bookmarks,
            record.replies,
            record.engagement_score,
            record.created_at
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved {len(records)} performance records to database")

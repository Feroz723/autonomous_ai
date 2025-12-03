"""
Run Daily Cycle Script

Orchestrates the full daily workflow:
1. Fetch new trends
2. Select top niche topics
3. Generate content (Tweets, Threads, CTAs)
4. Add to content queue
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from dataclasses import asdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trend_fetcher.fetch_trends import (
    get_raw_trends_from_source,
    normalize_trends,
    store_trends_to_sqlite
)
from src.niche_selector.select_topics import select_topics
from src.content_generator.generator import ContentGenerator
from src.content_generator.models import Topic, ContentItem

DB_PATH = "data/solopreneur.db"
QUEUE_FILE = "data/content_queue.json"

def save_queue(items: list[ContentItem]):
    """Appends new items to the content queue."""
    data = [asdict(item) for item in items]
    
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, 'r') as f:
                existing = json.load(f)
                data = existing + data
        except json.JSONDecodeError:
            pass
            
    with open(QUEUE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Added {len(items)} items to {QUEUE_FILE}")

def save_to_db(items: list[ContentItem]):
    """Saves generated content to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    count = 0
    for item in items:
        try:
            cursor.execute("""
                INSERT INTO generated_content (niche_score_id, content_type, content, generated_at)
                VALUES (?, ?, ?, ?)
            """, (
                item.topic_id, 
                item.type,
                item.content,
                item.created_at
            ))
            count += 1
        except Exception as e:
            print(f"⚠️ DB Error: {e}")
            
    conn.commit()
    conn.close()
    print(f"✅ Saved {count} items to database")

def main():
    # Force UTF-8 for stdout on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("="*60)
    print(f"🚀 STARTING DAILY CYCLE: {datetime.now()}")
    print("="*60)

    # 1. Fetch Trends
    print("\nSTEP 1: Fetching Trends...")
    try:
        raw_trends = get_raw_trends_from_source()
        normalized = normalize_trends(raw_trends)
        store_trends_to_sqlite(normalized, DB_PATH)
    except Exception as e:
        print(f"❌ Trend fetching failed: {e}")
        # Continue anyway if we have old data
    
    # 2. Select Topics
    print("\nSTEP 2: Selecting Topics...")
    top_topics_data = select_topics(db_path=DB_PATH, top_n=5)
    
    if not top_topics_data:
        print("❌ No topics found. Exiting.")
        return

    topics = [
        Topic(
            id=t['id'],
            text=t['topic'],
            source=t['source'],
            score=t['final_score'],
            keywords=t.get('keywords', [])
        )
        for t in top_topics_data
    ]

    # 3. Generate Content
    print("\nSTEP 3: Generating Content...")
    generator = ContentGenerator()
    new_content = []

    for topic in topics:
        print(f"  > {topic.text[:40]}...")
        
        # Generate Tweet
        new_content.append(generator.generate_tweet(topic))
        
        # Generate Thread (for top 2 topics)
        if topic in topics[:2]:
            new_content.append(generator.generate_thread(topic))
            
        # Generate CTA
        new_content.append(generator.generate_cta(topic))

    # 4. Save
    print("\nSTEP 4: Saving Output...")
    save_queue(new_content)
    save_to_db(new_content)
    
    print("\n✨ Daily cycle completed successfully!")

if __name__ == "__main__":
    main()

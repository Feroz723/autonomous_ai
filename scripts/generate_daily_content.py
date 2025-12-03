"""
Generate Daily Content Script

Orchestrates the content generation process:
1. Loads top topics from the database (via niche_selector).
2. Generates tweets and threads using ContentGenerator.
3. Saves output to data/content_queue.json and the database.
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from dataclasses import asdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.niche_selector.select_topics import select_topics
from src.content_generator.generator import ContentGenerator
from src.content_generator.models import Topic, ContentItem

DB_PATH = "data/solopreneur.db"
OUTPUT_FILE = "data/content_queue.json"

def save_to_json(items: list[ContentItem], filepath: str):
    """Saves content items to a JSON file."""
    data = [asdict(item) for item in items]
    
    # Load existing if any
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                existing = json.load(f)
                data = existing + data
        except json.JSONDecodeError:
            pass
            
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(items)} items to {filepath}")

def save_to_db(items: list[ContentItem], db_path: str):
    """Saves content items to the SQLite database."""
    conn = sqlite3.connect(db_path)
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
            print(f"Error saving to DB: {e}")
            
    conn.commit()
    conn.close()
    print(f"Saved {count} items to database")

def main():
    print("🚀 Starting Daily Content Generation...")
    
    # 1. Get Top Topics
    # We'll get top 5 topics
    top_topics_data = select_topics(db_path=DB_PATH, top_n=5)
    
    if not top_topics_data:
        print("No topics found. Run fetch_and_select_topics.py first.")
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
    
    generator = ContentGenerator()
    new_content = []

    # 2. Generate Content
    for topic in topics:
        print(f"Generating content for: {topic.text[:50]}...")
        
        # Generate 1 Tweet
        tweet = generator.generate_tweet(topic)
        new_content.append(tweet)
        
        # Generate 1 Thread (only for top 1 topic)
        if topic == topics[0]:
            thread = generator.generate_thread(topic)
            new_content.append(thread)
            
        # Generate 1 CTA
        cta = generator.generate_cta(topic)
        new_content.append(cta)

    # 3. Save Output
    save_to_json(new_content, OUTPUT_FILE)
    save_to_db(new_content, DB_PATH)
    
    print("✅ Content generation complete!")

if __name__ == "__main__":
    main()

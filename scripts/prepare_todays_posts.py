"""
Prepare Today's Posts Script

Selects content from the queue for today's schedule.
- Selects 3 tweets and 1 thread.
- Outputs to data/today_posts.txt.
- Optionally posts to Twitter API if enabled.
- Updates the content queue (removes used items).
"""

import sys
import os
import json
import yaml
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.scheduler_poster.post_to_twitter_api import TwitterPoster

QUEUE_FILE = "data/content_queue.json"
OUTPUT_FILE = "data/today_posts.txt"
CONFIG_FILE = "config/twitter_settings.yaml"

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, 'r') as f:
        return json.load(f)

def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

def main():
    # Force UTF-8 for stdout on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("📅 Preparing posts for today...")
    
    queue = load_queue()
    if not queue:
        print("❌ Content queue is empty! Run run_daily_cycle.py first.")
        return

    config = load_config()
    schedule_slots = config['schedule']['slots']
    
    # Selection logic: 1 Thread + (N-1) Tweets
    # We want to fill the slots.
    
    posts_for_today = []
    remaining_queue = []
    
    # Try to find 1 thread first
    thread_found = False
    
    # Separate threads and tweets
    threads = [item for item in queue if item['type'] == 'thread']
    tweets = [item for item in queue if item['type'] == 'tweet']
    ctas = [item for item in queue if item['type'] == 'cta']
    
    # Select 1 thread if available
    if threads:
        posts_for_today.append(threads[0])
        threads = threads[1:]
        thread_found = True
        
    # Fill remaining slots with tweets
    slots_needed = len(schedule_slots) - len(posts_for_today)
    
    if len(tweets) >= slots_needed:
        posts_for_today.extend(tweets[:slots_needed])
        tweets = tweets[slots_needed:]
    else:
        # Not enough tweets, take what we have
        posts_for_today.extend(tweets)
        tweets = []
        
    # Reconstruct queue with unused items
    # (We keep CTAs for now, maybe attach them to tweets later)
    remaining_queue = threads + tweets + ctas
    
    if not posts_for_today:
        print("⚠️ No suitable content found in queue.")
        return

    # Prepare output text
    output_text = f"📅 POSTS FOR {datetime.now().strftime('%Y-%m-%d')}\n"
    output_text += "=" * 40 + "\n\n"
    
    poster = TwitterPoster()
    
    for i, post in enumerate(posts_for_today):
        slot = schedule_slots[i] if i < len(schedule_slots) else "EXTRA"
        
        content = post['content']
        post_type = post['type'].upper()
        
        output_text += f"⏰ SLOT {i+1}: {slot} ({post_type})\n"
        output_text += "-" * 20 + "\n"
        output_text += content + "\n"
        output_text += "-" * 20 + "\n\n"
        
        # Post to API if enabled
        if config.get('enabled', False):
            print(f"🚀 Posting to Twitter ({slot})...")
            if post['type'] == 'thread':
                # Parse thread tweets
                # Assuming raw_data has 'tweets' list, or split by separator
                tweets_list = post.get('raw_data', {}).get('tweets', [])
                if not tweets_list:
                     # Fallback split
                     tweets_list = content.split('\n\n---\n\n')
                
                poster.post_thread(tweets_list)
            else:
                poster.post_tweet(content)
        else:
            print(f"📝 Scheduled {post_type} for {slot} (Dry Run)")

    # Save output file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_text)
    
    print(f"✅ Saved {len(posts_for_today)} posts to {OUTPUT_FILE}")
    
    # Update queue
    save_queue(remaining_queue)
    print(f"📉 Queue updated. Remaining items: {len(remaining_queue)}")

if __name__ == "__main__":
    main()

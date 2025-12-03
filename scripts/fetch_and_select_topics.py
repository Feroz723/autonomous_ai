"""
Fetch and Select Topics CLI Script

Runs the trend fetcher and niche selector, then displays top topics.

Usage:
    python scripts/fetch_and_select_topics.py [--top N] [--hours H]
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trend_fetcher.fetch_trends import (
    get_raw_trends_from_source,
    normalize_trends,
    store_trends_to_sqlite
)
from src.niche_selector.select_topics import (
    select_topics,
    print_top_topics,
    get_top_keywords
)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Fetch trending topics and select top niche-relevant ones'
    )
    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top topics to display (default: 10)'
    )
    parser.add_argument(
        '--hours',
        type=int,
        default=24,
        help='Hours to look back for trends (default: 24)'
    )
    parser.add_argument(
        '--skip-fetch',
        action='store_true',
        help='Skip fetching new trends, only select from existing'
    )
    parser.add_argument(
        '--db',
        type=str,
        default='data/solopreneur.db',
        help='Path to SQLite database (default: data/solopreneur.db)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🤖 AI SOLOPRENEUR BOT - TREND FETCHER & NICHE SELECTOR")
    print("=" * 80)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Fetch trends (unless skipped)
    if not args.skip_fetch:
        print("STEP 1: Fetching Trends")
        print("-" * 80)
        
        raw_trends = get_raw_trends_from_source()
        
        if not raw_trends:
            print("\n❌ No trends fetched. Exiting.")
            return 1
        
        # Normalize trends
        normalized = normalize_trends(raw_trends)
        print(f"✅ Normalized {len(normalized)} trends")
        
        # Store in database
        stored = store_trends_to_sqlite(normalized, args.db)
        
        if stored == 0:
            print("\n⚠️  No trends stored. Database may already contain these trends.")
        
        print()
    else:
        print("⏭️  Skipping trend fetching (using existing data)\n")
    
    # Step 2: Select top topics
    print("STEP 2: Selecting Top Topics")
    print("-" * 80)
    
    top_topics = select_topics(
        db_path=args.db,
        hours=args.hours,
        min_keyword_matches=1,
        top_n=args.top
    )
    
    if not top_topics:
        print("\n❌ No topics selected. Try fetching new trends or adjusting filters.")
        return 1
    
    # Display results
    print_top_topics(top_topics, show_details=True)
    
    # Show keyword analysis
    print("\n" + "=" * 80)
    print("📌 KEYWORD ANALYSIS")
    print("=" * 80)
    
    top_keywords = get_top_keywords(top_topics, top_n=15)
    
    if top_keywords:
        print("\nMost Common Keywords in Selected Topics:\n")
        for i, (keyword, count) in enumerate(top_keywords, 1):
            bar = "█" * min(count, 20)
            print(f"{i:2d}. {keyword:25s} {bar} ({count})")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"✓ Total topics selected: {len(top_topics)}")
    print(f"✓ Time range: Last {args.hours} hours")
    print(f"✓ Database: {args.db}")
    
    # Calculate source distribution
    sources = {}
    for topic in top_topics:
        source = topic['source']
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📍 Source Distribution:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {source}: {count}")
    
    # Calculate average scores
    avg_final = sum(t['final_score'] for t in top_topics) / len(top_topics)
    avg_engagement = sum(t['score'] for t in top_topics) / len(top_topics)
    
    print(f"\n📈 Average Scores:")
    print(f"  - Final Score: {avg_final:.2f}")
    print(f"  - Engagement: {avg_engagement:.0f}")
    
    print("\n" + "=" * 80)
    print(f"✅ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

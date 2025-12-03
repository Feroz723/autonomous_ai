"""
Update Topic Scores

Imports analytics CSV, calculates topic scores, and generates a report.
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analytics_engine.importer import import_analytics_csv, save_to_analytics_db
from src.analytics_engine.scorer import calculate_topic_scores, load_performance_records

DB_PATH = "data/analytics.sqlite"
REPORT_PATH = "data/analytics_report.md"

def generate_report(topic_scores: dict) -> str:
    """Generate markdown analytics report."""
    
    report = f"# Analytics Report - {datetime.now().strftime('%Y-%m-%d')}\n\n"
    
    # Sort by engagement score
    sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1].avg_engagement_score, reverse=True)
    
    # Top performers
    report += "## 🏆 Top Performing Topics\n\n"
    for topic, perf in sorted_topics[:5]:
        report += f"**{topic}**\n"
        report += f"- Avg Engagement Score: {perf.avg_engagement_score:.4f}\n"
        report += f"- Total Tweets: {perf.total_tweets}\n"
        report += f"- Avg Impressions: {perf.avg_impressions:.0f}\n"
        report += f"- Recommendation: {perf.get_recommendation()}\n\n"
    
    # Underperformers
    report += "## ⚠️ Underperforming Topics\n\n"
    underperformers = [t for t in sorted_topics if t[1].avg_engagement_score < 0.02]
    
    if underperformers:
        for topic, perf in underperformers:
            report += f"**{topic}**\n"
            report += f"- Avg Engagement Score: {perf.avg_engagement_score:.4f}\n"
            report += f"- Recommendation: {perf.get_recommendation()}\n\n"
    else:
        report += "*No underperforming topics found.*\n\n"
    
    # Recommendations
    report += "## 💡 Recommendations\n\n"
    
    boost_topics = [t[0] for t in sorted_topics if t[1].avg_engagement_score > 0.05]
    reduce_topics = [t[0] for t in sorted_topics if t[1].avg_engagement_score < 0.02]
    
    if boost_topics:
        report += f"**Focus more on:** {', '.join(boost_topics)}\n\n"
    if reduce_topics:
        report += f"**Reduce or rework:** {', '.join(reduce_topics)}\n\n"
    
    # Overall stats
    report += "## 📊 Overall Statistics\n\n"
    total_tweets = sum(p.total_tweets for p in topic_scores.values())
    avg_score = sum(p.avg_engagement_score for p in topic_scores.values()) / len(topic_scores) if topic_scores else 0
    
    report += f"- Total Tweets Analyzed: {total_tweets}\n"
    report += f"- Average Engagement Score: {avg_score:.4f}\n"
    report += f"- Topics Tracked: {len(topic_scores)}\n"
    
    return report

def main():
    # Force UTF-8 for stdout on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Update topic scores from analytics")
    parser.add_argument("--input", help="Path to Twitter analytics CSV")
    parser.add_argument("--db", default=DB_PATH, help="Analytics database path")
    args = parser.parse_args()
    
    print("📊 Starting Analytics Update...")
    
    # Import CSV if provided
    if args.input:
        if not os.path.exists(args.input):
            print(f"❌ CSV file not found: {args.input}")
            print("Creating example CSV...")
            
            # Create example CSV
            with open(args.input, 'w') as f:
                f.write("Tweet id,Tweet text,impressions,likes,retweets,bookmarks,replies,created_at\n")
                f.write("123,AI automation is changing the game for solopreneurs,1000,50,10,5,2,2025-12-01\n")
                f.write("124,Productivity hack: use AI to automate your workflows,800,40,8,4,1,2025-12-01\n")
                f.write("125,Side hustle ideas for 2025,1200,60,12,6,3,2025-12-02\n")
            
            print(f"✅ Created example: {args.input}")
            print("Edit it with real data and run again.")
            return
        
        print(f"\n📥 Importing analytics from: {args.input}")
        records = import_analytics_csv(args.input)
        print(f"✅ Loaded {len(records)} performance records")
        
        # Save to database
        save_to_analytics_db(records, args.db)
    
    # Load all records
    print(f"\n📊 Calculating topic scores...")
    records = load_performance_records(args.db)
    
    if not records:
        print("⚠️ No performance records found in database.")
        print("Import analytics CSV first with --input flag.")
        return
    
    # Calculate scores
    topic_scores = calculate_topic_scores(records)
    print(f"✅ Analyzed {len(topic_scores)} topics")
    
    # Generate report
    print(f"\n📝 Generating report...")
    report = generate_report(topic_scores)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ Report saved: {REPORT_PATH}")
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    print("\n💡 Next steps:")
    print("1. Review the report above")
    print("2. The niche selector will automatically use these scores")
    print("3. Re-run this script weekly to update scores")

if __name__ == "__main__":
    main()

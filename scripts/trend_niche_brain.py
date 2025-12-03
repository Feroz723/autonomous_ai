"""
Trend & Niche Brain

An intelligent agent that analyzes trends and analytics to recommend
daily content strategy for your AI solopreneur Twitter/X account.

Usage:
    python scripts/trend_niche_brain.py
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.content_generator.llm_client import get_llm_client

TRENDS_DB = "data/solopreneur.db"
ANALYTICS_DB = "data/analytics.sqlite"
ANALYTICS_REPORT = "data/analytics_report.md"
ARTIFACT_DIR = "data/trend_plans"

# Niche categories
NICHE_CATEGORIES = {
    'AI Tools': ['ai tool', 'chatgpt', 'claude', 'gemini', 'llm', 'gpt'],
    'AI Freelancing': ['freelance', 'freelancer', 'client', 'gig', 'upwork'],
    'AI Automation': ['automation', 'automate', 'workflow', 'zapier', 'n8n'],
    'Productivity': ['productivity', 'productive', 'efficiency', 'time management'],
    'Solopreneur': ['solopreneur', 'solo', 'indie hacker', 'founder', 'bootstrap'],
    'Side Hustle': ['side hustle', 'passive income', 'extra income', 'money'],
    'AI for Business': ['business', 'small business', 'startup', 'scale']
}

def load_recent_trends(db_path: str, hours: int = 24) -> list:
    """Load trends from the last N hours."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cutoff = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff.isoformat()
    
    cursor.execute("""
        SELECT topic, source, score, keywords, fetched_at
        FROM trends
        WHERE fetched_at >= ?
        ORDER BY score DESC
        LIMIT 50
    """, (cutoff_str,))
    
    trends = []
    for row in cursor.fetchall():
        trends.append({
            'topic': row[0],
            'source': row[1],
            'score': row[2],
            'keywords': row[3],
            'fetched_at': row[4]
        })
    
    conn.close()
    return trends

def load_analytics_insights() -> dict:
    """Load insights from analytics report."""
    insights = {
        'top_topics': [],
        'avg_engagement': 0.0
    }
    
    if not os.path.exists(ANALYTICS_REPORT):
        return insights
    
    with open(ANALYTICS_REPORT, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Simple parsing - look for topic names and scores
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('**') and i + 1 < len(lines):
                topic = line.strip('*').strip()
                # Look for engagement score in next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if 'Avg Engagement Score:' in lines[j]:
                        try:
                            score = float(lines[j].split(':')[1].strip())
                            insights['top_topics'].append({'topic': topic, 'score': score})
                        except:
                            pass
    
    return insights

def categorize_topic(topic: str) -> str:
    """Categorize a topic into a niche."""
    topic_lower = topic.lower()
    
    for niche, keywords in NICHE_CATEGORIES.items():
        for keyword in keywords:
            if keyword in topic_lower:
                return niche
    
    return "General AI"

def generate_daily_plan(trends: list, analytics: dict) -> dict:
    """Generate the daily content plan."""
    
    # Score and rank topics
    topic_scores = defaultdict(lambda: {'score': 0, 'sources': [], 'niche': ''})
    
    for trend in trends:
        topic = trend['topic']
        niche = categorize_topic(topic)
        
        # Base score from trend
        score = trend.get('score', 0)
        
        # Boost if topic performed well historically
        for hist_topic in analytics.get('top_topics', []):
            if hist_topic['topic'].lower() in topic.lower():
                score *= 1.5  # 50% boost for proven performers
        
        topic_scores[topic]['score'] += score
        topic_scores[topic]['sources'].append(trend['source'])
        topic_scores[topic]['niche'] = niche
    
    # Sort by score
    ranked_topics = sorted(topic_scores.items(), key=lambda x: x[1]['score'], reverse=True)
    
    # Select top 3-5
    selected_topics = ranked_topics[:5]
    
    # Generate content suggestions using LLM
    llm_client = get_llm_client()
    
    best_topic = selected_topics[0][0] if selected_topics else "AI Automation"
    
    # Generate tweet ideas
    tweet_prompt = f"""Generate 5 single tweet ideas about "{best_topic}" for solopreneurs.

Requirements:
- Actionable and beginner-friendly
- Money-making angles
- 70% educational, 20% story, 10% sales
- Each tweet should be unique

Format: Just list the 5 tweet concepts, one per line."""
    
    tweet_ideas = llm_client.generate_text(tweet_prompt)
    
    # Generate thread idea
    thread_prompt = f"""Generate 1 thread idea (5-7 tweets) about "{best_topic}".

Make it:
- Step-by-step actionable
- Beginner-friendly
- Include a soft CTA at the end

Format: Just describe the thread concept in 2-3 sentences."""
    
    thread_idea = llm_client.generate_text(thread_prompt)
    
    # Generate product idea
    product_prompt = f"""Suggest 1 digital product or lead magnet idea related to "{best_topic}".

Make it:
- Easy to create
- High perceived value
- Solves a specific problem

Format: Just describe the product in 2-3 sentences."""
    
    product_idea = llm_client.generate_text(product_prompt)
    
    return {
        'selected_topics': selected_topics,
        'tweet_ideas': tweet_ideas,
        'thread_idea': thread_idea,
        'product_idea': product_idea
    }

def create_trend_plan_artifact(plan: dict) -> str:
    """Create the daily trend plan artifact."""
    
    today = datetime.now().strftime('%Y_%m_%d')
    filename = f"TREND_PLAN_{today}.md"
    
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    filepath = os.path.join(ARTIFACT_DIR, filename)
    
    content = f"""# Trend & Niche Plan - {datetime.now().strftime('%B %d, %Y')}

## 🎯 Chosen Topics (Ranked)

"""
    
    for i, (topic, data) in enumerate(plan['selected_topics'], 1):
        content += f"### {i}. {topic}\n"
        content += f"- **Niche**: {data['niche']}\n"
        content += f"- **Score**: {data['score']:.2f}\n"
        content += f"- **Sources**: {', '.join(set(data['sources']))}\n"
        content += f"- **Reason**: {'High historical performance + trending' if data['score'] > 100 else 'Currently trending'}\n\n"
    
    content += f"""## ✍️ Content Suggestions

### Single Tweets (5)
{plan['tweet_ideas']}

### Thread Idea (1)
{plan['thread_idea']}

### Product/Lead Magnet Idea
{plan['product_idea']}

---

## 📊 Content Mix Target
- 70% Educational
- 20% Story/Personal
- 10% Sales/Promotion

## 🎬 Next Steps
1. Review the chosen topics above
2. Use the tweet ideas as inspiration
3. Generate content with: `python scripts/generate_daily_content.py`
4. Review and schedule posts

*Generated by Trend & Niche Brain*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def main():
    # Force UTF-8 for stdout on Windows
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("🧠 Trend & Niche Brain - Analyzing...")
    print("="*60)
    
    # Load data
    print("\n📊 Loading trends from last 24 hours...")
    trends = load_recent_trends(TRENDS_DB, hours=24)
    print(f"✅ Found {len(trends)} recent trends")
    
    print("\n📈 Loading analytics insights...")
    analytics = load_analytics_insights()
    print(f"✅ Loaded insights on {len(analytics.get('top_topics', []))} topics")
    
    # Generate plan
    print("\n🎯 Generating daily content plan...")
    plan = generate_daily_plan(trends, analytics)
    
    # Create artifact
    print("\n📝 Creating trend plan artifact...")
    filepath = create_trend_plan_artifact(plan)
    print(f"✅ Saved to: {filepath}")
    
    # Display summary
    print("\n" + "="*60)
    print("🏆 TOP 3 TOPICS FOR TODAY:")
    print("="*60)
    for i, (topic, data) in enumerate(plan['selected_topics'][:3], 1):
        print(f"{i}. {topic} ({data['niche']}) - Score: {data['score']:.2f}")
    
    print("\n💡 Review the full plan at:")
    print(f"   {filepath}")
    print("\n🚀 Ready to create content!")

if __name__ == "__main__":
    main()

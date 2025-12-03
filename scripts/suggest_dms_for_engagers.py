"""
DM Suggestion Generator for Engagers

Reads a CSV of people who engaged with your content and generates
personalized DM suggestions using AI + templates.

Usage:
    python scripts/suggest_dms_for_engagers.py --input data/engagers.csv
"""

import sys
import os
import csv
import sqlite3
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lead_capture.lead_models import Lead
from src.lead_capture.templates import get_template_suggestions
from src.content_generator.llm_client import get_llm_client

DB_PATH = "data/leads.sqlite"
OUTPUT_PATH = "data/dm_suggestions.csv"

def init_leads_db(db_path: str):
    """Initialize the leads database if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT UNIQUE NOT NULL,
            source TEXT,
            status TEXT DEFAULT 'new',
            last_message TEXT,
            engagement_score INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Leads database initialized: {db_path}")

def save_lead(lead: Lead, db_path: str):
    """Save or update a lead in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO leads (handle, source, status, engagement_score, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(handle) DO UPDATE SET
                engagement_score = engagement_score + 1,
                updated_at = ?
        """, (
            lead.handle,
            lead.source,
            lead.status,
            lead.engagement_score,
            lead.notes,
            lead.created_at,
            lead.updated_at,
            lead.updated_at
        ))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Error saving lead {lead.handle}: {e}")
    finally:
        conn.close()

def generate_dm_suggestions(handle: str, context: str, llm_client) -> dict:
    """Generate personalized DM suggestions for an engager."""
    
    # Get template-based suggestions
    templates = get_template_suggestions(context, goal="engagement")
    
    # Optionally enhance with LLM (if not using dummy)
    # For now, we'll use templates directly and let LLM add personality
    
    suggestions = {}
    
    for template_type, template_text in templates.items():
        # Replace {name} placeholder with handle
        personalized = template_text.replace("{name}", f"@{handle}")
        suggestions[template_type] = personalized
    
    return suggestions

def main():
    parser = argparse.ArgumentParser(description="Generate DM suggestions for engagers")
    parser.add_argument("--input", default="data/engagers.csv", help="Input CSV file")
    parser.add_argument("--output", default=OUTPUT_PATH, help="Output CSV file")
    args = parser.parse_args()
    
    print("🚀 Starting DM Suggestion Generator...")
    
    # Initialize database
    init_leads_db(DB_PATH)
    
    # Load engagers
    if not os.path.exists(args.input):
        print(f"❌ Input file not found: {args.input}")
        print("Creating example file...")
        
        # Create example engagers.csv
        with open(args.input, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['handle', 'tweet_url', 'engagement_type', 'context'])
            writer.writerow(['john_doe', 'https://twitter.com/you/status/123', 'reply', 'AI automation'])
            writer.writerow(['jane_smith', 'https://twitter.com/you/status/124', 'like', 'productivity hacks'])
            writer.writerow(['tech_founder', 'https://twitter.com/you/status/125', 'retweet', 'solopreneur journey'])
        
        print(f"✅ Created example file: {args.input}")
        print("Edit it with real data and run again.")
        return
    
    engagers = []
    with open(args.input, 'r') as f:
        reader = csv.DictReader(f)
        engagers = list(reader)
    
    print(f"📊 Loaded {len(engagers)} engagers")
    
    # Generate suggestions
    llm_client = get_llm_client()
    results = []
    
    for engager in engagers:
        handle = engager.get('handle', '').strip()
        context = engager.get('context', 'your content').strip()
        engagement_type = engager.get('engagement_type', 'engagement').strip()
        
        if not handle:
            continue
        
        print(f"  > Generating DMs for @{handle}...")
        
        # Generate suggestions
        suggestions = generate_dm_suggestions(handle, context, llm_client)
        
        # Save lead
        lead = Lead(
            handle=handle,
            source=f"twitter_{engagement_type}",
            status="new",
            engagement_score=1,
            notes=f"Interested in: {context}"
        )
        save_lead(lead, DB_PATH)
        
        # Add to results
        for template_type, dm_text in suggestions.items():
            results.append({
                'handle': handle,
                'template_type': template_type,
                'suggested_dm': dm_text,
                'context': context,
                'confidence': 'high' if template_type == 'followup' else 'medium'
            })
    
    # Write output
    if results:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['handle', 'template_type', 'suggested_dm', 'context', 'confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"✅ Saved {len(results)} DM suggestions to {args.output}")
    else:
        print("⚠️ No suggestions generated")
    
    print("✨ Done!")

if __name__ == "__main__":
    main()

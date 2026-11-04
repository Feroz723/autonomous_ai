"""
Database Initialization Script

Creates the SQLite database and all necessary tables for the AI Solopreneur Bot.
"""

import os
import sqlite3


def init_database(db_path="data/solopreneur.db"):
    """Initialize the database with all required tables."""
    parent = os.path.dirname(os.path.abspath(db_path))
    os.makedirs(parent, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        print(f"Initializing database at: {db_path}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                source TEXT,
                score INTEGER,
                url TEXT,
                keywords TEXT,
                hashtags TEXT,
                engagement_score INTEGER,
                tweet_count INTEGER,
                category TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created table: trends")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS niche_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend_id INTEGER,
                relevance_score REAL,
                engagement_potential REAL,
                historical_multiplier REAL,
                final_score REAL,
                selected BOOLEAN DEFAULT 0,
                scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trend_id) REFERENCES trends(id)
            )
        """)
        print("✓ Created table: niche_scores")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche_score_id INTEGER,
                content_type TEXT,
                content TEXT,
                hashtags TEXT,
                cta_link TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted BOOLEAN DEFAULT 0,
                FOREIGN KEY (niche_score_id) REFERENCES niche_scores(id)
            )
        """)
        print("✓ Created table: generated_content")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posted_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                tweet_id TEXT,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_time TIMESTAMP,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (content_id) REFERENCES generated_content(id)
            )
        """)
        print("✓ Created table: posted_content")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                twitter_handle TEXT,
                email TEXT,
                interest_area TEXT,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                engagement_score INTEGER,
                followed_up BOOLEAN DEFAULT 0
            )
        """)
        print("✓ Created table: leads")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                topic TEXT,
                file_path TEXT,
                gumroad_url TEXT,
                price INTEGER,
                downloads INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created table: products")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                impressions INTEGER,
                likes INTEGER,
                retweets INTEGER,
                replies INTEGER,
                link_clicks INTEGER,
                leads_generated INTEGER,
                engagement_rate REAL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES posted_content(id)
            )
        """)
        print("✓ Created table: analytics")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT,
                level TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created table: system_logs")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trends_fetched ON trends(fetched_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_niche_selected ON niche_scores(selected)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_posted ON generated_content(posted)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posted_status ON posted_content(status)")
        print("✓ Created indexes")

        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        print("\n✅ Database initialized successfully!")
        print(f"📊 Total tables created: {len(tables)}")
        print(f"📁 Database location: {os.path.abspath(db_path)}")


if __name__ == "__main__":
    init_database()

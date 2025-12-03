"""
MASTER ORCHESTRATION SCRIPT
Runs the complete AI Solopreneur Bot pipeline end-to-end.

This is the MAIN entry point for full autonomy.
"""

import sys
import os
import subprocess
import logging
from datetime import datetime

# Setup logging
log_dir = "data/logs"
os.makedirs(log_dir, exist_ok=True)

# Force UTF-8 for stdout
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/master_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_script(script_path, description, args=None):
    """Run a Python script and handle errors."""
    logger.info(f"{'='*60}")
    logger.info(f"RUNNING: {description}")
    logger.info(f"{'='*60}")
    
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
            capture_output=True,
            text=True,
            encoding='utf-8',  # Explicitly use UTF-8 for reading output
            timeout=300
        )
        
        if result.stdout:
            logger.info(result.stdout)
        
        if result.returncode != 0:
            logger.error(f"ERROR in {description}")
            if result.stderr:
                logger.error(result.stderr)
            return False
        
        logger.info(f"✅ {description} completed successfully")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"TIMEOUT: {description} took too long")
        return False
    except Exception as e:
        logger.error(f"EXCEPTION in {description}: {str(e)}")
        return False

def main():
    logger.info("🚀 AI SOLOPRENEUR BOT - MASTER ORCHESTRATION")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("="*60)
    
    # Ensure required directories exist
    required_dirs = ["data/trend_plans", "data/analytics", "products", "data/logs"]
    for dir_path in required_dirs:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"✓ Directory ready: {dir_path}")
    
    # PHASE 1: Strategic Planning
    logger.info("\n📊 PHASE 1: STRATEGIC PLANNING")
    if not run_script("scripts/trend_niche_brain.py", "Trend & Niche Brain Analysis"):
        logger.warning("⚠️ Trend Brain failed, continuing with fallback...")
    
    # PHASE 2: Content Generation
    logger.info("\n✍️ PHASE 2: CONTENT GENERATION")
    if not run_script("scripts/run_daily_cycle.py", "Daily Content Cycle"):
        logger.error("❌ Content generation failed - CRITICAL")
        return False
    
    # PHASE 3: Post Preparation
    logger.info("\n📅 PHASE 3: POST PREPARATION")
    if not run_script("scripts/prepare_todays_posts.py", "Today's Post Preparation"):
        logger.warning("⚠️ Post preparation failed, check content queue")
    
    # PHASE 4: Analytics Update (if data available)
    logger.info("\n📈 PHASE 4: ANALYTICS UPDATE")
    analytics_csv = "data/twitter_analytics.csv"
    if os.path.exists(analytics_csv):
        run_script("scripts/update_topic_scores.py", "Analytics Update", 
                  ["--input", analytics_csv])
    else:
        logger.info("ℹ️ No analytics CSV found, skipping analytics update")
    
    # PHASE 5: Summary
    logger.info("\n" + "="*60)
    logger.info("✨ MASTER ORCHESTRATION COMPLETE")
    logger.info(f"Finished at: {datetime.now()}")
    logger.info("="*60)
    
    logger.info("\n📋 NEXT STEPS:")
    logger.info("1. Review: data/today_posts.txt")
    logger.info("2. Check: data/content_queue.json")
    logger.info("3. View plan: data/trend_plans/TREND_PLAN_*.md")
    logger.info("4. Post content to Twitter/X")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

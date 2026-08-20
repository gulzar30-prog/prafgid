# backend/scheduler.py
import sys
import time
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from backend.database import SessionLocal
from backend.models import IntelligenceItem
from backend.collectors.rss_collector import fetch_rss_feed
from backend.processors.cleaner import is_duplicate
from backend.processors.ai_summarizer import summarize_and_score
from datetime import datetime
import yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_sources():
    """Load sources from config/sources.yaml"""
    sources_path = project_root / "config" / "sources.yaml"
    if not sources_path.exists():
        logger.error(f"Sources file not found: {sources_path}")
        return []
    
    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config.get("sources", [])
    except Exception as e:
        logger.error(f"Error loading sources: {e}")
        return []

def collect_and_process():
    """Collect and process data from all sources"""
    logger.info("=" * 50)
    logger.info("Starting collection cycle")
    
    sources = load_sources()
    if not sources:
        logger.warning("No sources found to collect")
        return
    
    db = SessionLocal()
    total_saved = 0
    
    for source in sources:
        if source.get("type") != "rss":
            continue
        
        source_name = source.get("name", "Unknown")
        source_url = source.get("url", "")
        categories = source.get("category", [])
        
        logger.info(f"Fetching: {source_name} from {source_url}")
        
        try:
            entries = fetch_rss_feed(source_url)
            logger.info(f"  Found {len(entries)} entries")
            
            for entry in entries:
                title = entry.get("title", "")
                if not title:
                    continue
                    
                # Check for duplicates
                if is_duplicate(db, title, entry.get("content", "")):
                    logger.debug(f"  Skipping duplicate: {title[:50]}...")
                    continue
                
                # Prepare content for AI summarization
                full_text = entry.get("content") or entry.get("summary") or title
                
                # Use non-AI summarizer (keyword-based)
                try:
                    ai_result = summarize_and_score(full_text, title)
                    summary = ai_result.get("summary", "No summary available")
                    scores = ai_result.get("scores", {})
                    relevance = ai_result.get("overall_relevance", 50)
                    detected_categories = ai_result.get("categories", categories)
                except Exception as e:
                    logger.warning(f"Processing failed: {e}")
                    summary = "Processing failed"
                    relevance = 50
                    detected_categories = categories
                
                # Create database entry
                item = IntelligenceItem(
                    title=title,
                    content=full_text,
                    summary=summary,
                    source_name=source_name,
                    source_url=entry.get("link", ""),
                    published_at=datetime.utcnow(),
                    category=detected_categories,
                    relevance_score=relevance,
                    importance_score=scores.get("importance", 50) if isinstance(scores, dict) else 50,
                    processed_data=ai_result if isinstance(ai_result, dict) else {}
                )
                
                try:
                    db.add(item)
                    total_saved += 1
                    logger.info(f"  ✅ Saved: {title[:50]}...")
                except Exception as e:
                    logger.error(f"  ❌ Error saving item: {e}")
            
            db.commit()
            logger.info(f"  ✅ Completed: {source_name} (saved {total_saved} new items)")
            
        except Exception as e:
            logger.error(f"  ❌ Error processing {source_name}: {e}")
            db.rollback()
    
    db.close()
    logger.info(f"✅ Collection cycle completed. Total new items saved: {total_saved}")
    logger.info("=" * 50)

def run_once():
    """Run one collection cycle (for testing)"""
    logger.info("Running single collection cycle...")
    collect_and_process()

def run_scheduler():
    """Run the scheduler continuously"""
    logger.info("🚀 Scheduler started. Press Ctrl+C to stop.")
    logger.info("Collection will run every 15 minutes.")
    
    # Run once immediately
    collect_and_process()
    
    # Then run every 15 minutes
    try:
        while True:
            time.sleep(900)  # 15 minutes
            collect_and_process()
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped by user.")

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        run_scheduler()
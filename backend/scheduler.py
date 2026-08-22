# backend/scheduler.py
import sys
import re
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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

_MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1
)}

def parse_published(entry):
    """Best-effort published date. Some feeds (e.g. Stata Headlines) omit the
    year from their pubDate, which feedparser can't parse into published_parsed."""
    published_parsed = entry.get("published_parsed")
    if published_parsed:
        return datetime(*published_parsed[:6])

    match = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\s+(\d{2}):(\d{2}):(\d{2})", entry.get("published", ""))
    if match:
        day, mon, hh, mm, ss = match.groups()
        month = _MONTHS.get(mon)
        if month:
            year = datetime.utcnow().year
            try:
                candidate = datetime(year, month, int(day), int(hh), int(mm), int(ss))
                if candidate > datetime.utcnow():
                    candidate = candidate.replace(year=year - 1)
                return candidate
            except ValueError:
                pass

    return datetime.utcnow()

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
                    
                if is_duplicate(db, title, entry.get("content", "")):
                    logger.debug(f"  Skipping duplicate: {title[:50]}...")
                    continue
                
                full_text = entry.get("content") or entry.get("summary") or title
                
                try:
                    ai_result = summarize_and_score(full_text, title)
                    summary = ai_result.get("summary", "No summary available")
                    relevance = ai_result.get("overall_relevance", 50)
                    detected_categories = sorted(set(categories) | set(ai_result.get("categories", [])))
                except Exception as e:
                    logger.warning(f"Processing failed: {e}")
                    summary = "Processing failed"
                    relevance = 50
                    detected_categories = categories

                published_at = parse_published(entry)

                item = IntelligenceItem(
                    title=title,
                    content=full_text,
                    summary=summary,
                    source_name=source_name,
                    source_url=entry.get("link", ""),
                    published_at=published_at,
                    category=detected_categories,
                    relevance_score=relevance,
                    importance_score=50,
                    processed_data={}
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

# No scheduler loop – you call collect_and_process() manually from the app.
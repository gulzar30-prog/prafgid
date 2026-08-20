# backend/collectors/rss_collector.py
import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def fetch_rss_feed(url: str) -> List[Dict[str, Any]]:
    """Fetch and parse an RSS feed, return list of entries."""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:20]:  # limit per run
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "published_parsed": entry.get("published_parsed"),
                "summary": entry.get("summary", ""),
                "content": entry.get("content", [{"value": ""}])[0].get("value", ""),
                "source_name": feed.feed.get("title", "Unknown RSS"),
            })
        return items
    except Exception as e:
        logger.error(f"RSS fetch error for {url}: {e}")
        return []
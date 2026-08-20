# test_feed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.collectors.rss_collector import fetch_rss_feed

url = "https://www.secp.gov.pk/feed/rss.asp?type=IslamicBanking"
items = fetch_rss_feed(url)
print(f"Fetched {len(items)} items")
for item in items[:3]:
    print(item["title"])
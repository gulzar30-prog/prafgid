# check_full.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models import IntelligenceItem

db = SessionLocal()

# Count
total = db.query(IntelligenceItem).count()
print(f"Total items: {total}")

# Show first 5 with all fields
items = db.query(IntelligenceItem).limit(5).all()
for item in items:
    print("-" * 40)
    print(f"ID: {item.id}")
    print(f"Title: {item.title[:50]}...")
    print(f"Published_at: {item.published_at}")
    print(f"Category: {item.category}")
    print(f"Relevance: {item.relevance_score}")

db.close()
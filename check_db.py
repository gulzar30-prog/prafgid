# check_db.py
import sys
import os
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models import IntelligenceItem

db = SessionLocal()
count = db.query(IntelligenceItem).count()
print(f"Items in DB: {count}")

# Show first 3 items
items = db.query(IntelligenceItem).limit(3).all()
for item in items:
    print(f"- {item.title[:50]}... (Relevance: {item.relevance_score})")

db.close()
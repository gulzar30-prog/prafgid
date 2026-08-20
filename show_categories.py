# show_categories.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.database import SessionLocal
from backend.models import IntelligenceItem

db = SessionLocal()
items = db.query(IntelligenceItem).limit(10).all()
for item in items:
    print(f"Title: {item.title[:40]}...")
    print(f"Categories: {item.category}")
    print("-" * 40)
db.close()
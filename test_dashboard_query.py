# test_dashboard_query.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models import IntelligenceItem

db = SessionLocal()
recent = db.query(IntelligenceItem).order_by(IntelligenceItem.published_at.desc()).limit(20).all()
print(f"Dashboard query returned: {len(recent)} items")
for item in recent[:3]:
    print(f" - {item.title[:30]}...")
db.close()
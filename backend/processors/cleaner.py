# backend/processors/cleaner.py
from sqlalchemy.orm import Session
from backend.models import IntelligenceItem
import hashlib

def compute_text_hash(text: str) -> str:
    return hashlib.md5(text[:200].encode()).hexdigest()

def is_duplicate(session: Session, title: str, content: str) -> bool:
    # Simple title‑based deduplication – you can improve later
    existing = session.query(IntelligenceItem).filter(
        IntelligenceItem.title.ilike(f"%{title[:50]}%")
    ).first()
    return existing is not None
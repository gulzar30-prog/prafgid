# backend/models.py
from sqlalchemy import Column, String, DateTime, Float, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class IntelligenceItem(Base):
    __tablename__ = "intelligence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source_name = Column(String(100))
    source_url = Column(String(500))
    published_at = Column(DateTime)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
    category = Column(JSON)          # list of category strings
    relevance_score = Column(Float)
    importance_score = Column(Float)
    urgency_score = Column(Float)
    research_relevance = Column(Float)
    professional_relevance = Column(Float)
    is_duplicate = Column(Boolean, default=False)
    duplicate_group_id = Column(UUID(as_uuid=True), nullable=True)
    raw_data = Column(JSON)
    processed_data = Column(JSON)

    def __repr__(self):
        return f"<Item {self.title[:50]}...>"
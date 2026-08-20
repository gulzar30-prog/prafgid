# app/app.py
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

import streamlit as st
from backend.database import SessionLocal
from backend.models import IntelligenceItem
import pandas as pd
from datetime import datetime
from sqlalchemy import text

st.set_page_config(page_title="PRAFGID", layout="wide")

st.sidebar.title("🧠 PRAFGID")
st.sidebar.caption("Personal Intelligence Centre")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "🇵🇰 Pakistan & Finance",
        "🕌 Islamic Finance",
        "🤖 AI & Research",
        "🌱 Sustainability"
    ]
)

db = SessionLocal()

def get_items_by_categories(category_list):
    """Return IntelligenceItem objects that have any of the given categories."""
    if not category_list:
        return []
    placeholders = ",".join([f"'{cat}'" for cat in category_list])
    sql = text(f"""
        SELECT * FROM intelligence_items
        WHERE EXISTS (
            SELECT 1 FROM json_each(intelligence_items.category)
            WHERE value IN ({placeholders})
        )
        ORDER BY published_at DESC
        LIMIT 50
    """)
    # Execute and map to model
    result = db.execute(sql)
    # Convert rows to IntelligenceItem objects
    items = []
    for row in result:
        # row is a Row object; we can create a dict and then map
        # Simpler: get ids and query
        # But we can also use db.query with from_statement
        pass
    # Better: use from_statement
    items = db.query(IntelligenceItem).from_statement(sql).all()
    return items

def display_items(items, title):
    if not items:
        st.info("No items found in this category.")
        return
    for item in items:
        with st.expander(f"{item.title}  (Relevance: {item.relevance_score:.0f})"):
            st.write(item.summary or "No summary available.")
            st.caption(f"Source: {item.source_name} | Published: {item.published_at}")
            if item.source_url:
                st.link_button("View Source", item.source_url)

# ==================== HOME ====================
if page == "🏠 Home":
    st.title("📊 Personal Intelligence Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M')}")
    total_count = db.query(IntelligenceItem).count()
    st.write(f"🔍 Total items in database: {total_count}")
    recent = db.query(IntelligenceItem).order_by(IntelligenceItem.published_at.desc()).limit(50).all()
    db.close()
    if recent:
        critical = [item for item in recent if item.relevance_score and item.relevance_score > 80]
        if critical:
            st.subheader("🔴 Critical Alerts")
            for item in critical[:5]:
                st.markdown(f"**{item.title}**  (Relevance: {item.relevance_score:.0f}/100)")
                st.caption(item.summary[:200] + "..." if item.summary else "")
                st.write("---")
        data = []
        for item in recent[:20]:
            data.append({
                "Title": item.title,
                "Source": item.source_name,
                "Category": ", ".join(item.category) if item.category else "",
                "Relevance": item.relevance_score,
                "Published": item.published_at.strftime("%Y-%m-%d %H:%M") if item.published_at else "",
            })
        df = pd.DataFrame(data)
        st.subheader("📰 Latest Intelligence")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data collected yet. Run the scheduler to populate.")

# ==================== PAKISTAN & FINANCE ====================
elif page == "🇵🇰 Pakistan & Finance":
    st.title("🇵🇰 Pakistan & Financial Intelligence")
    items = get_items_by_categories(["pakistan", "finance", "business"])
    db.close()
    display_items(items, "Pakistan & Finance")

# ==================== ISLAMIC FINANCE ====================
elif page == "🕌 Islamic Finance":
    st.title("🕌 Islamic Finance Intelligence")
    items = get_items_by_categories(["islamic_finance"])
    db.close()
    display_items(items, "Islamic Finance")

# ==================== AI & RESEARCH ====================
elif page == "🤖 AI & Research":
    st.title("🤖 AI & Research Intelligence")
    items = get_items_by_categories(["ai", "research"])
    db.close()
    display_items(items, "AI & Research")

# ==================== SUSTAINABILITY ====================
elif page == "🌱 Sustainability":
    st.title("🌱 Sustainability & ESG Intelligence")
    items = get_items_by_categories(["sustainability", "esg"])
    db.close()
    display_items(items, "Sustainability")
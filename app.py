# app.py
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
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

db = SessionLocal()

def get_items_by_categories(category_list, limit=50):
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
        LIMIT {limit}
    """)
    return db.query(IntelligenceItem).from_statement(sql).all()

def display_items(items):
    if not items:
        st.info("No items found in this category yet.")
        return
    for item in items:
        with st.expander(f"{item.title}  (Relevance: {item.relevance_score:.0f})"):
            st.write(item.summary or "No summary available.")
            st.caption(f"Source: {item.source_name} | Published: {item.published_at}")
            if item.source_url:
                st.link_button("View Source", item.source_url)

def category_tab(title, categories):
    st.title(title)
    display_items(get_items_by_categories(categories))

# ==================== TABS ====================
(
    tab_home,
    tab_pakistan,
    tab_islamic,
    tab_markets,
    tab_research,
    tab_software,
    tab_ai_fintech,
    tab_regulatory,
) = st.tabs(
    [
        "🏠 Home",
        "🇵🇰 Pakistan Finance",
        "🕌 Islamic Finance",
        "📈 Financial Markets",
        "📚 Research & Publications",
        "🧮 Software Updates",
        "🤖 AI, FinTech & Digital Finance",
        "📜 Regulatory & Policy",
    ]
)

# ---- Home ----
with tab_home:
    st.title("📊 Personal Intelligence Dashboard")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M')}")
    total_count = db.query(IntelligenceItem).count()
    st.write(f"🔍 Total items in database: {total_count}")
    recent = db.query(IntelligenceItem).order_by(IntelligenceItem.published_at.desc()).limit(50).all()
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

# ---- Pakistan Finance ----
with tab_pakistan:
    category_tab("🇵🇰 Pakistan Financial Intelligence", ["pakistan", "finance", "business"])

# ---- Islamic Finance ----
with tab_islamic:
    category_tab("🕌 Islamic Finance Intelligence", ["islamic_finance"])

# ---- Financial Markets ----
with tab_markets:
    category_tab("📈 Financial Markets Intelligence", ["financial_markets"])

# ---- Research & Publications ----
with tab_research:
    category_tab("📚 Research & Publications", ["research"])

# ---- Software Updates ----
with tab_software:
    st.title("🧮 Statistical & Econometric Software Updates")
    software_sections = [
        ("R / RStudio", ["software_r"]),
        ("Stata", ["software_stata"]),
        ("EViews", ["software_eviews"]),
        ("SPSS", ["software_spss"]),
        ("SmartPLS", ["software_smartpls"]),
        ("Python", ["software_python"]),
    ]
    software_tabs = st.tabs([name for name, _ in software_sections])
    for st_tab, (name, cats) in zip(software_tabs, software_sections):
        with st_tab:
            display_items(get_items_by_categories(cats))

# ---- AI, FinTech & Digital Finance ----
with tab_ai_fintech:
    category_tab("🤖 AI, FinTech & Digital Finance", ["ai", "fintech"])

# ---- Regulatory & Policy ----
with tab_regulatory:
    category_tab("📜 Regulatory & Policy Updates", ["regulatory_policy"])

db.close()

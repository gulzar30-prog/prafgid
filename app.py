# app.py
import sys
import html
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

st.set_page_config(page_title="PRAFGID", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .prafgid-hero {
        background: linear-gradient(135deg, #0E7C66 0%, #14A085 100%);
        padding: 1.75rem 2rem;
        border-radius: 14px;
        color: #FFFFFF;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(14,124,102,0.25);
    }
    .prafgid-hero h1 { margin: 0; font-size: 1.9rem; }
    .prafgid-hero p { margin: 0.35rem 0 0 0; opacity: 0.92; font-size: 0.95rem; }

    .stat-card {
        background: #FFFFFF; border: 1px solid #E3E8E6; border-radius: 12px;
        padding: 1rem 0.5rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stat-card .stat-value { font-size: 1.6rem; font-weight: 700; color: #0E7C66; }
    .stat-card .stat-label {
        font-size: 0.75rem; color: #667; text-transform: uppercase; letter-spacing: .04em;
    }

    .item-card {
        background: #FFFFFF; border-radius: 12px; border: 1px solid #E7EBEA;
        border-left: 5px solid #0E7C66;
        padding: 1rem 1.25rem; margin-bottom: 0.85rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .item-card .item-title { font-size: 1.02rem; font-weight: 600; color: #1A1A2E; margin: 0 0 .4rem 0; }
    .item-card .item-meta { font-size: 0.78rem; color: #8A8F98; margin-bottom: .55rem; }
    .item-card .item-summary { font-size: 0.9rem; color: #3A3F47; line-height: 1.45; margin-bottom: .5rem; }
    .item-card a.item-link { font-size: 0.82rem; font-weight: 600; color: #0E7C66; text-decoration: none; }
    .item-card a.item-link:hover { text-decoration: underline; }

    .badge {
        display: inline-block; padding: 0.15rem 0.55rem; border-radius: 999px;
        font-size: 0.72rem; font-weight: 600; margin-right: 0.5rem;
    }
    .badge-high { background: #E3F6EC; color: #0E7C66; }
    .badge-mid  { background: #FFF3D6; color: #8A6100; }
    .badge-low  { background: #F1F2F4; color: #666B73; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🧠 PRAFGID")
st.sidebar.caption("Personal Research & Financial Intelligence Dashboard")

db = SessionLocal()

# Accent colors per tab, used for the item card's left border
ACCENTS = {
    "top_news": "#C0392B",
    "pakistan": "#0E7C66",
    "islamic_finance": "#127A6B",
    "financial_markets": "#1F6FB2",
    "research": "#6B4FA0",
    "software": "#D97706",
    "ai_fintech": "#4338CA",
    "regulatory_policy": "#475569",
}

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

def relevance_badge(score):
    score = score or 0
    if score >= 70:
        css, label = "badge-high", "High"
    elif score >= 40:
        css, label = "badge-mid", "Medium"
    else:
        css, label = "badge-low", "Low"
    return f'<span class="badge {css}">{label} · {score:.0f}</span>'

def render_item_card(item, accent="#0E7C66"):
    published = item.published_at.strftime("%b %d, %Y · %H:%M") if item.published_at else "Unknown date"
    summary = html.escape((item.summary or "No summary available.").strip())
    source_url = item.source_url or ""
    link_html = ""
    if source_url.startswith("http://") or source_url.startswith("https://"):
        link_html = f'<a class="item-link" href="{html.escape(source_url)}" target="_blank" rel="noopener noreferrer">Read source →</a>'
    st.markdown(f"""
    <div class="item-card" style="border-left-color:{accent}">
        <div class="item-title">{html.escape(item.title)}</div>
        <div class="item-meta">{relevance_badge(item.relevance_score)}📰 {html.escape(item.source_name or "Unknown")} &nbsp;·&nbsp; 🗓 {published}</div>
        <div class="item-summary">{summary}</div>
        {link_html}
    </div>
    """, unsafe_allow_html=True)

def display_items(items, accent="#0E7C66"):
    if not items:
        st.info("No items found in this category yet.")
        return
    for item in items:
        render_item_card(item, accent=accent)

def category_tab(title, categories, accent="#0E7C66", limit=50):
    st.title(title)
    display_items(get_items_by_categories(categories, limit=limit), accent=accent)

# ==================== TABS ====================
(
    tab_home,
    tab_top_news,
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
        "🌍 Top News",
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
    st.markdown(f"""
    <div class="prafgid-hero">
        <h1>📊 Personal Intelligence Board</h1>
        <p>Pakistan &amp; Islamic finance, global markets, research, statistical software, and world news — last updated {datetime.now().strftime('%b %d, %Y at %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)

    total_count = db.query(IntelligenceItem).count()
    recent = db.query(IntelligenceItem).order_by(IntelligenceItem.published_at.desc()).limit(50).all()
    critical = [item for item in recent if item.relevance_score and item.relevance_score > 80]
    sources_count = db.query(IntelligenceItem.source_name).distinct().count()

    c1, c2, c3, c4 = st.columns(4)
    for col, value, label in zip(
        [c1, c2, c3, c4],
        [total_count, len(critical), sources_count, 8],
        ["Total Items", "Critical Alerts", "Active Sources", "Coverage Areas"],
    ):
        col.markdown(
            f'<div class="stat-card"><div class="stat-value">{value}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    if recent:
        if critical:
            st.subheader("🔴 Critical Alerts")
            for item in critical[:5]:
                render_item_card(item, accent="#C0392B")

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
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data collected yet. Run the scheduler to populate.")

# ---- Top News ----
with tab_top_news:
    category_tab("🌍 Top News", ["top_news"], accent=ACCENTS["top_news"], limit=60)

# ---- Pakistan Finance ----
with tab_pakistan:
    category_tab("🇵🇰 Pakistan Financial Intelligence", ["pakistan", "finance", "business"], accent=ACCENTS["pakistan"])

# ---- Islamic Finance ----
with tab_islamic:
    category_tab("🕌 Islamic Finance Intelligence", ["islamic_finance"], accent=ACCENTS["islamic_finance"])

# ---- Financial Markets ----
with tab_markets:
    category_tab("📈 Financial Markets Intelligence", ["financial_markets"], accent=ACCENTS["financial_markets"])

# ---- Research & Publications ----
with tab_research:
    category_tab("📚 Research & Publications", ["research"], accent=ACCENTS["research"])

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
            display_items(get_items_by_categories(cats), accent=ACCENTS["software"])

# ---- AI, FinTech & Digital Finance ----
with tab_ai_fintech:
    category_tab("🤖 AI, FinTech & Digital Finance", ["ai", "fintech"], accent=ACCENTS["ai_fintech"])

# ---- Regulatory & Policy ----
with tab_regulatory:
    category_tab("📜 Regulatory & Policy Updates", ["regulatory_policy"], accent=ACCENTS["regulatory_policy"])

db.close()

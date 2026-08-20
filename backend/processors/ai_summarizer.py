# backend/processors/ai_summarizer.py
import re
from collections import Counter

def summarize_and_score(text: str, title: str, categories_weights: dict = None):
    """
    Non‑AI summarization and scoring using keywords and simple heuristics.
    """
    if not text:
        text = title
    
    # 1. Generate a simple summary (first 200 characters)
    summary = text[:200].strip() + "..." if len(text) > 200 else text.strip()
    
    # 2. Load category keywords from config/categories.yaml
    import yaml
    from pathlib import Path
    
    config_path = Path(__file__).parent.parent.parent / "config" / "categories.yaml"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cat_config = yaml.safe_load(f)
            categories = cat_config.get("categories", {})
    except:
        categories = {}  # fallback empty
    
    # 3. Score each category based on keyword matches in text (and title)
    scores = {}
    matched_categories = []
    
    for cat_name, cat_info in categories.items():
        keywords = cat_info.get("keywords", [])
        weight = cat_info.get("weight", 50)
        
        # Count occurrences of keywords in the full text (case‑insensitive)
        text_lower = text.lower()
        title_lower = title.lower()
        match_count = 0
        for kw in keywords:
            kw_lower = kw.lower()
            # Boost if keyword appears in title
            if kw_lower in title_lower:
                match_count += 2
            # Count in text
            match_count += text_lower.count(kw_lower)
        
        # Normalize score between 0‑100 based on matches
        raw_score = min(100, match_count * 10)  # each match = 10 points, capped at 100
        # Apply category weight
        final_score = min(100, raw_score * (weight / 100))
        scores[cat_name] = round(final_score, 2)
        
        if final_score >= 30:   # threshold to consider it relevant
            matched_categories.append(cat_name)
    
    # 4. Overall relevance = max score across all categories
    overall = max(scores.values()) if scores else 50
    
    # 5. Generate "Why it matters" – generic
    why_matters = f"This article discusses {title}. Based on your interests in {', '.join(matched_categories) if matched_categories else 'various topics'}, it may be relevant to your research."
    
    return {
        "summary": summary,
        "scores": scores,
        "categories": matched_categories,
        "why_matters": why_matters,
        "overall_relevance": overall
    }
import re

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "love",
    "loved", "happy", "helpful", "fast", "easy", "perfect",
    "satisfied", "smooth", "quick", "friendly", "recommend",
}

NEGATIVE_WORDS = {
    "bad", "poor", "terrible", "awful", "hate", "hated",
    "angry", "slow", "late", "delay", "delayed", "broken",
    "issue", "problem", "refund", "expensive", "difficult",
    "unhappy", "disappointed", "disappointing", "worst",
}

CATEGORY_RULES = {
    "Delivery": [
        "delivery", "deliver", "shipping", "shipment", "arrive",
        "arrived", "late", "delay", "delayed", "courier",
    ],
    "Customer Support": [
        "support", "agent", "customer service", "helpdesk",
        "representative", "response", "respond",
    ],
    "Pricing": [
        "price", "pricing", "cost", "expensive", "cheap",
        "discount", "refund", "fee", "charge",
    ],
    "Product Experience": [
        "app", "website", "interface", "ui", "ux", "login",
        "checkout", "feature", "navigation", "easy", "difficult",
    ],
    "Product Quality": [
        "quality", "broken", "defect", "damaged", "product",
        "performance", "works", "working",
    ],
}

THEME_RULES = {
    "Delivery delays": ["delivery", "shipping", "late", "delay", "courier"],
    "Customer support": ["support", "agent", "service", "response", "help"],
    "Pricing concerns": ["price", "pricing", "cost", "expensive", "charge", "fee"],
    "Product quality": ["quality", "broken", "damaged", "defect", "performance"],
    "User experience": ["app", "website", "interface", "checkout", "login", "navigation"],
}


def _words(text):
    return set(re.findall(r"[a-zA-Z']+", text.lower()))


def analyze_feedback(message, rating=None):
    text = message.lower()
    words = _words(message)

    positive_hits = len(words & POSITIVE_WORDS)
    negative_hits = len(words & NEGATIVE_WORDS)

    if rating is not None:
        if rating <= 2:
            sentiment = "Negative"
        elif rating >= 4:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"
    elif negative_hits > positive_hits:
        sentiment = "Negative"
    elif positive_hits > negative_hits:
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    if sentiment == "Positive":
        score = min(1.0, 0.55 + (positive_hits * 0.08))
    elif sentiment == "Negative":
        score = max(-1.0, -0.55 - (negative_hits * 0.08))
    else:
        score = 0.0

    category = "General"
    category_score = 0
    for name, keywords in CATEGORY_RULES.items():
        hits = sum(1 for keyword in keywords if keyword in text)
        if hits > category_score:
            category = name
            category_score = hits

    theme = "General"
    theme_score = 0
    for name, keywords in THEME_RULES.items():
        hits = sum(1 for keyword in keywords if keyword in text)
        if hits > theme_score:
            theme = name
            theme_score = hits

    if sentiment == "Negative" and (rating is not None and rating <= 2):
        priority = "High"
    elif sentiment == "Negative":
        priority = "Medium"
    else:
        priority = "Low"

    keywords = sorted(
        (words & (POSITIVE_WORDS | NEGATIVE_WORDS)),
        key=lambda value: value,
    )[:10]

    return {
        "sentiment": sentiment,
        "sentiment_score": round(score, 2),
        "category": category,
        "theme": theme,
        "priority": priority,
        "keywords": keywords,
    }

import pytest
from feedbackx.core.review_scraper_engine import ReviewScraperEngine
from feedbackx.core.aspect_sentiment_analyzer import AspectSentimentAnalyzer

def test_aspect_analyzer():
    reviews = ReviewScraperEngine.scrape_feedback(50)
    clusters = AspectSentimentAnalyzer.analyze_reviews(reviews)
    assert len(clusters) >= 3
    assert -1.0 <= clusters[0].sentiment_score <= 1.0
    assert clusters[0].churn_risk_score > 0

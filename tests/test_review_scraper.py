import pytest
from feedbackx.core.review_scraper_engine import ReviewScraperEngine

def test_review_scraper():
    reviews = ReviewScraperEngine.scrape_feedback(100)
    assert len(reviews) == 100
    assert reviews[0].review_id.startswith("REV-")
    assert 1 <= reviews[0].rating_stars <= 5

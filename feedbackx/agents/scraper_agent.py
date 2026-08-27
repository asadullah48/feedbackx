from typing import List
from feedbackx.core.models import CustomerReviewItem
from feedbackx.core.review_scraper_engine import ReviewScraperEngine

class ScraperAgent:
    """
    ScraperAgent: Scrapes, deduplicates, and filters spam across multi-channel customer reviews.
    """
    def __init__(self):
        self.name = "ScraperAgent"
        self.version = "1.0.0"

    def scrape_multi_channel_reviews(self, count: int = 1500) -> List[CustomerReviewItem]:
        return ReviewScraperEngine.scrape_feedback(count)

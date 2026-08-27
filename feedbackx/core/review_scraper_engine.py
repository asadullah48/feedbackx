from typing import List
from feedbackx.core.models import CustomerReviewItem, PlatformSource

class ReviewScraperEngine:
    """
    ReviewScraperEngine: Simulates high-throughput multi-platform customer review ingestion (thousands of reviews).
    """
    @staticmethod
    def scrape_feedback(count: int = 1500) -> List[CustomerReviewItem]:
        sample_templates = [
            (PlatformSource.G2_CROWD, 2, "Role-based permissions (RBAC) are missing for enterprise multi-tenancy. We might cancel our plan.", "Enterprise User"),
            (PlatformSource.APP_STORE, 5, "Blazing fast UI and clean design! The keyboard shortcuts are a massive productivity booster.", "Pro Creator"),
            (PlatformSource.TRUSTPILOT, 1, "Exporting CSV datasets times out when records exceed 50,000 rows. Please fix ASAP.", "Enterprise User"),
            (PlatformSource.REDDIT, 3, "Great concept but lacks dark mode and offline local caching support.", "Free Tier"),
            (PlatformSource.GOOGLE_PLAY, 4, "Reliable app, would love to see automated webhook integrations with Slack and Discord.", "Pro Creator")
        ]
        
        reviews = []
        for i in range(count):
            tmpl = sample_templates[i % len(sample_templates)]
            reviews.append(CustomerReviewItem(
                review_id=f"REV-{tmpl[0].value[:3]}-{i+1:04d}",
                source=tmpl[0],
                rating_stars=tmpl[1],
                review_text=f"{tmpl[2]} (Feedback Ref #{i+1})",
                user_segment=tmpl[3]
            ))
        return reviews

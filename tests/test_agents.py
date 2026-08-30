import pytest
from feedbackx.agents.scraper_agent import ScraperAgent
from feedbackx.agents.analyzer_agent import AnalyzerAgent
from feedbackx.agents.insight_agent import InsightAgent

def test_all_feedback_agents():
    scraper = ScraperAgent()
    analyzer = AnalyzerAgent()
    insighter = InsightAgent()

    reviews = scraper.scrape_multi_channel_reviews(100)
    clusters = analyzer.analyze_feedback_aspects(reviews)
    roadmap = insighter.synthesize_roadmap(clusters, total_reviews=len(reviews))

    assert len(reviews) == 100
    assert len(clusters) >= 3
    assert len(roadmap) >= 2

    # Roadmap must be a real function of the data: sorted by RICE score, every score
    # positive, and the top item must actually be the highest-priority one in the list.
    rice_scores = [item.rice_score for item in roadmap]
    assert rice_scores == sorted(rice_scores, reverse=True)
    assert all(score > 0 for score in rice_scores)
    assert roadmap[0].rice_score == max(rice_scores)
    assert roadmap[0].urgency_tier == "P0_IMMEDIATE"

def test_roadmap_scales_with_review_volume():
    """Mention counts (and therefore RICE reach) must move with input size, not stay fixed."""
    scraper = ScraperAgent()
    analyzer = AnalyzerAgent()

    small_reviews = scraper.scrape_multi_channel_reviews(50)
    large_reviews = scraper.scrape_multi_channel_reviews(500)

    small_clusters = {c.aspect_name: c for c in analyzer.analyze_feedback_aspects(small_reviews)}
    large_clusters = {c.aspect_name: c for c in analyzer.analyze_feedback_aspects(large_reviews)}

    shared_aspect = next(iter(small_clusters))
    assert large_clusters[shared_aspect].mention_count > small_clusters[shared_aspect].mention_count

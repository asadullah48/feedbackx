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
    roadmap = insighter.synthesize_roadmap(clusters)

    assert len(reviews) == 100
    assert len(clusters) >= 3
    assert len(roadmap) >= 2
    assert roadmap[0].rice_score > 80.0

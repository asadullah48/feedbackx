import pytest
from feedbackx.orchestration.feedbackx_engine import FeedbackXEngine

def test_feedbackx_engine_pipeline():
    engine = FeedbackXEngine()
    report = engine.generate_market_intelligence(review_count=500)
    assert report.total_reviews_analyzed == 500
    assert len(report.aspect_clusters) >= 3
    assert len(report.prioritized_roadmap) >= 2
    assert report.analysis_latency_ms > 0

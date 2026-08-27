"""
FeedbackX: Autonomous Customer Feedback Mining & Market Intelligence Multi-Agent Framework
"""

__version__ = "1.0.0"

from feedbackx.agents.scraper_agent import ScraperAgent
from feedbackx.agents.analyzer_agent import AnalyzerAgent
from feedbackx.agents.insight_agent import InsightAgent
from feedbackx.orchestration.feedbackx_engine import FeedbackXEngine

__all__ = [
    "ScraperAgent",
    "AnalyzerAgent",
    "InsightAgent",
    "FeedbackXEngine"
]

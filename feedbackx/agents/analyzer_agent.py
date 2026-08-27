from typing import List
from feedbackx.core.models import CustomerReviewItem, AspectSentimentCluster
from feedbackx.core.aspect_sentiment_analyzer import AspectSentimentAnalyzer

class AnalyzerAgent:
    """
    AnalyzerAgent: Performs Aspect-Based Sentiment Analysis (ABSA) and churn risk quantification.
    """
    def __init__(self):
        self.name = "AnalyzerAgent"
        self.version = "1.0.0"

    def analyze_feedback_aspects(self, reviews: List[CustomerReviewItem]) -> List[AspectSentimentCluster]:
        return AspectSentimentAnalyzer.analyze_reviews(reviews)

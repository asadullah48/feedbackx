from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class PlatformSource(str, Enum):
    APP_STORE = "APP_STORE"
    GOOGLE_PLAY = "GOOGLE_PLAY"
    G2_CROWD = "G2_CROWD"
    TRUSTPILOT = "TRUSTPILOT"
    REDDIT = "REDDIT"

class FeedbackSentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    FEATURE_REQUEST = "FEATURE_REQUEST"

class CustomerReviewItem(BaseModel):
    review_id: str
    source: PlatformSource
    rating_stars: int # 1 to 5
    review_text: str
    user_segment: str # "Enterprise User" | "Free Tier" | "Pro Creator"
    scraped_at: float = Field(default_factory=time.time)

class AspectSentimentCluster(BaseModel):
    cluster_id: str
    aspect_name: str # e.g. "Onboarding UX", "Export Latency", "Role Permissions"
    sentiment: FeedbackSentiment
    mention_count: int
    sentiment_score: float # -1.0 to +1.0
    churn_risk_score: float # 0.0 to 100.0
    sample_snippets: List[str]

class FeatureRoadmapItem(BaseModel):
    feature_id: str
    feature_title: str
    rice_score: float # Reach * Impact * Confidence / Effort
    urgency_tier: str # P0_IMMEDIATE | P1_NEXT_SPRINT | P2_BACKLOG
    pain_point_addressed: str
    estimated_churn_reduction_percent: float

class MarketIntelligenceReport(BaseModel):
    report_id: str
    total_reviews_analyzed: int
    average_customer_csat: float
    aspect_clusters: List[AspectSentimentCluster]
    prioritized_roadmap: List[FeatureRoadmapItem]
    executive_strategic_summary: str
    analysis_latency_ms: float
    generated_at: float = Field(default_factory=time.time)

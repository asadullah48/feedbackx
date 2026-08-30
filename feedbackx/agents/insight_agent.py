from typing import List
from feedbackx.core.models import AspectSentimentCluster, FeatureRoadmapItem, FeedbackSentiment

# Engineering-effort estimate (person-months) inferred from the aspect name. Checked in
# order, so more specific phrases must be listed before their generic parents.
_EFFORT_HEURISTICS = [
    ("rbac", 3.0), ("sso", 3.0), ("access control", 3.0),
    ("export", 2.5), ("performance", 2.5), ("latency", 2.5),
    ("webhook", 1.5), ("integration", 1.5),
    ("personalization", 1.0), ("offline", 1.0),
    ("ui responsiveness", 0.75), ("design polish", 0.75),
]
_DEFAULT_EFFORT_MONTHS = 1.5

_REACH_BASE = 1000  # RICE "Reach" normalized to a 1,000-customer cohort per review-mention share


class InsightAgent:
    """
    InsightAgent: Turns AnalyzerAgent's real aspect clusters into an actual RICE-scored
    roadmap (Reach x Impact x Confidence / Effort), so results move when the input does
    instead of returning a fixed list.
    """

    def __init__(self):
        self.name = "InsightAgent"
        self.version = "1.1.0"

    @staticmethod
    def _estimate_effort_months(aspect_name: str) -> float:
        lowered = aspect_name.lower()
        for keyword, months in _EFFORT_HEURISTICS:
            if keyword in lowered:
                return months
        return _DEFAULT_EFFORT_MONTHS

    def synthesize_roadmap(self, clusters: List[AspectSentimentCluster], total_reviews: int) -> List[FeatureRoadmapItem]:
        total_reviews = max(total_reviews, 1)
        # Purely positive aspects with no churn signal are wins to celebrate, not roadmap items.
        candidates = [c for c in clusters if not (c.sentiment == FeedbackSentiment.POSITIVE and c.churn_risk_score < 10)]

        roadmap: List[FeatureRoadmapItem] = []
        for cluster in candidates:
            reach = (cluster.mention_count / total_reviews) * _REACH_BASE
            impact = 0.5 + (cluster.churn_risk_score / 100) * 2.5       # RICE impact: 0.5 (low) .. 3.0 (massive)
            confidence = 0.7 + min(cluster.mention_count, 50) / 50 * 0.3  # more mentions -> more confidence
            effort = self._estimate_effort_months(cluster.aspect_name)

            rice_raw = (reach * impact * confidence) / effort
            rice_score = round(rice_raw / 10, 1)  # scaled into a 0-100 priority index for the dashboard

            if rice_score >= 15:
                tier = "P0_IMMEDIATE"
            elif rice_score >= 7:
                tier = "P1_NEXT_SPRINT"
            else:
                tier = "P2_BACKLOG"

            churn_reduction = round(min(18.0, (cluster.churn_risk_score / 100) * confidence * 20), 1)

            roadmap.append(FeatureRoadmapItem(
                feature_id=f"FEAT-{cluster.cluster_id}",
                feature_title=f"Address: {cluster.aspect_name}",
                rice_score=rice_score,
                urgency_tier=tier,
                pain_point_addressed=cluster.sample_snippets[0] if cluster.sample_snippets else cluster.aspect_name,
                estimated_churn_reduction_percent=churn_reduction,
            ))

        roadmap.sort(key=lambda item: item.rice_score, reverse=True)
        return roadmap

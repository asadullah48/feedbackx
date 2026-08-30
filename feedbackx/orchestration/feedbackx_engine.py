import time
from feedbackx.core.models import MarketIntelligenceReport
from feedbackx.core.llm_provider import OllamaProvider
from feedbackx.agents.scraper_agent import ScraperAgent
from feedbackx.agents.analyzer_agent import AnalyzerAgent
from feedbackx.agents.insight_agent import InsightAgent


class FeedbackXEngine:
    """
    FeedbackXEngine: Coordinates the feedback mining pipeline (Scrape -> Analyze ABSA -> Prioritize Roadmap)
    and synthesizes the executive summary, optionally enriched by a local free-tier LLM (Ollama).
    """
    def __init__(self):
        self.scraper = ScraperAgent()
        self.analyzer = AnalyzerAgent()
        self.insighter = InsightAgent()
        self.llm = OllamaProvider()

    def generate_market_intelligence(self, review_count: int = 1500) -> MarketIntelligenceReport:
        t0 = time.time()

        reviews = self.scraper.scrape_multi_channel_reviews(review_count)
        clusters = self.analyzer.analyze_feedback_aspects(reviews)
        roadmap = self.insighter.synthesize_roadmap(clusters, total_reviews=len(reviews))

        latency = (time.time() - t0) * 1000.0
        csat = round(sum(r.rating_stars for r in reviews) / len(reviews), 2) if reviews else 0.0
        summary = self._build_executive_summary(reviews, clusters, roadmap)

        return MarketIntelligenceReport(
            report_id=f"INTEL-{abs(hash((review_count, len(reviews)))) % 10000}",
            total_reviews_analyzed=len(reviews),
            average_customer_csat=csat,
            aspect_clusters=clusters,
            prioritized_roadmap=roadmap,
            executive_strategic_summary=summary,
            analysis_latency_ms=max(15.0, latency),
        )

    def _build_executive_summary(self, reviews, clusters, roadmap) -> str:
        platform_count = len({r.source for r in reviews}) if reviews else 0
        top_cluster = clusters[0] if clusters else None
        top_items = roadmap[:3]
        total_churn_reduction = round(sum(item.estimated_churn_reduction_percent for item in top_items), 1)

        deterministic_summary = (
            f"FeedbackX analyzed {len(reviews)} customer reviews across {platform_count} platforms. "
            + (
                f"Primary churn driver is '{top_cluster.aspect_name}' ({top_cluster.churn_risk_score:.1f}% churn risk score). "
                if top_cluster else ""
            )
            + (
                f"Shipping the top {len(top_items)} roadmap item(s) is projected to reduce overall churn by {total_churn_reduction:.1f}%."
                if top_items else "No actionable roadmap items were identified from this review sample."
            )
        )

        if not self.llm.enabled:
            return deterministic_summary

        prompt = (
            "You are a product strategy analyst. In 2-3 concise sentences, write an executive "
            "summary of this customer feedback intelligence report. Be direct and specific. "
            "Output ONLY the summary sentences themselves — no preamble, no headers, no meta-commentary.\n\n"
            f"Reviews analyzed: {len(reviews)} across {platform_count} platforms.\n"
            f"Top churn-risk aspect: {top_cluster.aspect_name if top_cluster else 'N/A'} "
            f"({top_cluster.churn_risk_score if top_cluster else 0}% churn risk).\n"
            f"Top roadmap priorities: {', '.join(item.feature_title for item in top_items) or 'none'}.\n"
            f"Projected churn reduction if top items ship: {total_churn_reduction}%."
        )
        llm_summary = self.llm.generate_executive_summary(prompt)
        return llm_summary or deterministic_summary

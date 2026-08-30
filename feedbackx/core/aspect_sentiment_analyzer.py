import re
from typing import List, Dict
from feedbackx.core.models import CustomerReviewItem, AspectSentimentCluster, FeedbackSentiment

# Each aspect is matched against review text via substring keywords, and carries an
# engineering-effort estimate (person-months) consumed later by InsightAgent's RICE math.
_ASPECTS: List[Dict] = [
    {
        "name": "Enterprise RBAC & SSO Access Control",
        "keywords": ["rbac", "role-based", "permission", "multi-tenan", "sso", "saml", "okta", "access control"],
    },
    {
        "name": "Bulk Dataset Export Performance",
        "keywords": ["export", "csv", "times out", "timeout", "50,000", "large dataset"],
    },
    {
        "name": "Third-Party Integrations & Webhooks",
        "keywords": ["webhook", "integration", "slack", "discord", "zapier"],
    },
    {
        "name": "UI Responsiveness & Design Polish",
        "keywords": ["blazing", "clean design", "keyboard shortcut", "productivity booster", "sleek", "smooth ui"],
    },
    {
        "name": "Personalization & Offline Support Gaps",
        "keywords": ["dark mode", "offline", "local caching", "caching support"],
    },
]
_GENERAL_ASPECT_NAME = "General Product Experience"

# Lightweight sentiment lexicon (VADER-style but dependency-free) blended with star rating.
_POSITIVE_WORDS = {
    "blazing", "fast", "clean", "great", "love", "reliable", "booster", "sleek", "smooth",
    "excellent", "amazing", "intuitive", "helpful", "responsive", "robust", "good", "nice",
    "awesome", "impressive", "polished", "solid",
}
_NEGATIVE_WORDS = {
    "missing", "cancel", "fix", "lacks", "lack", "bug", "broken", "slow", "frustrating",
    "frustrated", "crash", "fail", "failed", "poor", "bad", "annoying", "confusing",
    "expensive", "limited", "disappointed", "terrible", "awful", "worst",
}
# Phrases signalling "please build this" rather than a plain complaint/compliment.
_REQUEST_CUES = ["would love", "lacks", "lack of", "missing", "wish", "hope to see", "request", "requires"]

_CHURN_BASE_BY_RATING = {1: 70, 2: 50, 3: 20, 4: 5, 5: 0}
_REF_SUFFIX_RE = re.compile(r"\s*\(Feedback Ref #\d+\)\s*$")


def _word_hits(text: str, words: set) -> int:
    return sum(1 for w in words if re.search(rf"\b{re.escape(w)}\b", text))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class AspectSentimentAnalyzer:
    """
    AspectSentimentAnalyzer: Extracts product aspects via keyword matching, then computes
    sentiment and churn-risk directly from each review's text and rating (no canned output).
    A keyword-lexicon approach was chosen over a heavier NLP dependency so the whole engine
    stays free-tier and dependency-light; see LLMProvider for an optional Ollama upgrade path.
    """

    @staticmethod
    def analyze_reviews(reviews: List[CustomerReviewItem]) -> List[AspectSentimentCluster]:
        buckets: Dict[str, List[CustomerReviewItem]] = {}

        for review in reviews:
            lowered = review.review_text.lower()
            matched_any = False
            for aspect in _ASPECTS:
                if any(keyword in lowered for keyword in aspect["keywords"]):
                    buckets.setdefault(aspect["name"], []).append(review)
                    matched_any = True
            if not matched_any:
                buckets.setdefault(_GENERAL_ASPECT_NAME, []).append(review)

        clusters: List[AspectSentimentCluster] = []
        for aspect_name, matched_reviews in buckets.items():
            review_sentiments = []
            review_churns = []
            cue_hits = 0
            snippets: List[str] = []

            for review in matched_reviews:
                lowered = review.review_text.lower()
                pos_hits = _word_hits(lowered, _POSITIVE_WORDS)
                neg_hits = _word_hits(lowered, _NEGATIVE_WORDS)

                rating_component = (review.rating_stars - 3) / 2  # -1..1
                if pos_hits or neg_hits:
                    lexicon_component = (pos_hits - neg_hits) / (pos_hits + neg_hits)
                    sentiment = _clamp(0.5 * rating_component + 0.5 * lexicon_component, -1.0, 1.0)
                else:
                    sentiment = rating_component
                review_sentiments.append(sentiment)

                base_churn = _CHURN_BASE_BY_RATING.get(review.rating_stars, 20)
                segment_multiplier = 1.25 if review.user_segment == "Enterprise User" else 1.0
                review_churns.append(min(100.0, base_churn * segment_multiplier + 8 * neg_hits))

                if any(cue in lowered for cue in _REQUEST_CUES):
                    cue_hits += 1

                clean_snippet = _REF_SUFFIX_RE.sub("", review.review_text)
                if clean_snippet not in snippets:
                    snippets.append(clean_snippet)

            mention_count = len(matched_reviews)
            avg_sentiment = round(sum(review_sentiments) / mention_count, 2)
            churn_risk = round(sum(review_churns) / mention_count, 1)

            cue_fraction = cue_hits / mention_count
            if cue_fraction >= 0.3:
                sentiment_label = FeedbackSentiment.FEATURE_REQUEST
            elif avg_sentiment <= -0.15:
                sentiment_label = FeedbackSentiment.NEGATIVE
            else:
                sentiment_label = FeedbackSentiment.POSITIVE

            clusters.append(AspectSentimentCluster(
                cluster_id="ASP-PENDING",  # reassigned below once sorted
                aspect_name=aspect_name,
                sentiment=sentiment_label,
                mention_count=mention_count,
                sentiment_score=avg_sentiment,
                churn_risk_score=churn_risk,
                sample_snippets=snippets[:3],
            ))

        clusters.sort(key=lambda c: c.churn_risk_score, reverse=True)
        for idx, cluster in enumerate(clusters, start=1):
            cluster.cluster_id = f"ASP-{idx:02d}"

        return clusters

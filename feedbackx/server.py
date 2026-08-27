import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from feedbackx.core.models import MarketIntelligenceReport, CustomerReviewItem
from feedbackx.orchestration.feedbackx_engine import FeedbackXEngine
from feedbackx.core.review_scraper_engine import ReviewScraperEngine

app = FastAPI(
    title="FeedbackX Market Intelligence Gateway",
    version="1.0.0",
    description="Autonomous Customer Feedback Mining & Market Intelligence Multi-Agent Framework"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = FeedbackXEngine()

# Mount Static UI Files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"service": "FeedbackX", "status": "active", "docs": "/docs"}

@app.get("/healthz")
def healthz():
    return {"status": "healthy", "service": "FeedbackX", "version": "1.0.0"}

@app.get("/readyz")
def readyz():
    return {"status": "ready", "market_intelligence_agents_active": 3}

@app.get("/api/v1/feedback/sample-reviews", response_model=List[CustomerReviewItem])
def get_sample_reviews(count: int = 10):
    return ReviewScraperEngine.scrape_feedback(count)

@app.post("/api/v1/feedback/generate-intelligence", response_model=MarketIntelligenceReport)
def generate_intelligence(review_count: int = 1500):
    return engine.generate_market_intelligence(review_count)

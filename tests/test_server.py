from fastapi.testclient import TestClient
from feedbackx.server import app

client = TestClient(app)

def test_server_dashboard_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "FeedbackX" in res.text

def test_server_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_server_readyz():
    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["market_intelligence_agents_active"] == 3

def test_server_sample_reviews_api():
    res = client.get("/api/v1/feedback/sample-reviews?count=15")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 15

def test_server_generate_intelligence_api():
    res = client.post("/api/v1/feedback/generate-intelligence?review_count=200")
    assert res.status_code == 200
    data = res.json()
    assert data["total_reviews_analyzed"] == 200
    assert len(data["prioritized_roadmap"]) >= 2

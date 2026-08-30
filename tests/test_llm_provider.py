import pytest
from feedbackx.core.llm_provider import OllamaProvider

def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("FEEDBACKX_ENABLE_LLM", raising=False)
    provider = OllamaProvider()
    assert provider.enabled is False
    assert provider.is_available() is False
    assert provider.generate_executive_summary("hello") is None

def test_enabled_but_unreachable_fails_soft(monkeypatch):
    monkeypatch.setenv("FEEDBACKX_ENABLE_LLM", "true")
    monkeypatch.setenv("FEEDBACKX_OLLAMA_HOST", "http://127.0.0.1:1")  # nothing listens here
    provider = OllamaProvider()
    assert provider.enabled is True
    assert provider.is_available() is False
    assert provider.generate_executive_summary("hello") is None

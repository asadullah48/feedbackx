import os
from typing import Optional
import httpx


class OllamaProvider:
    """
    OllamaProvider: Optional free-tier LLM enrichment via a local Ollama instance
    (https://ollama.com) — no API keys, no per-token billing.

    Fully opt-in and fails soft: if Ollama isn't running, isn't installed, or the
    request times out, callers get None and fall back to the deterministic
    template-based summary. This matters because the hosted live demo has no local
    LLM to reach, so the product must degrade gracefully rather than error out.
    """

    def __init__(self):
        self.enabled = os.getenv("FEEDBACKX_ENABLE_LLM", "false").strip().lower() in ("1", "true", "yes")
        self.host = os.getenv("FEEDBACKX_OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("FEEDBACKX_OLLAMA_MODEL", "llama3.2")
        self._probe_timeout = 0.6   # keep API responses snappy when Ollama is absent
        self._generate_timeout = 30.0

    def is_available(self) -> bool:
        """Cheap reachability probe — used by /api/v1/system/llm-status for UI transparency."""
        if not self.enabled:
            return False
        try:
            resp = httpx.get(f"{self.host}/api/tags", timeout=self._probe_timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def generate_executive_summary(self, prompt: str) -> Optional[str]:
        if not self.enabled:
            return None
        try:
            resp = httpx.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 200},  # bound response length so it stays fast
                },
                timeout=self._generate_timeout,
            )
            resp.raise_for_status()
            text = resp.json().get("response", "").strip()
            return text or None
        except Exception:
            # Network hiccup, model not pulled, Ollama not running, etc. — never break the request.
            return None

"""Shared settings. Each value can be overridden with an environment variable."""
import os
from pathlib import Path

WEBSITE_URL = os.getenv("TEST_WEBSITE", "https://example.com")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "reports"))
PAGE_TIMEOUT_MS = 60000

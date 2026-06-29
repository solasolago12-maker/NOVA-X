import os
import sys
import pytest

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.ai_engine import AIEngine


def test_local_provider_missing_model():
    cfg = {"provider": "local", "model_path": ""}
    engine = AIEngine(cfg)
    # When no model path is provided, the local provider should not be initialised
    assert engine._model_client is None


def test_local_chat_without_model_returns_error():
    cfg = {"provider": "local", "model_path": ""}
    engine = AIEngine(cfg)
    resp = engine.chat("Hello", mode="chat", history=None)
    assert resp.startswith("[ERROR]")

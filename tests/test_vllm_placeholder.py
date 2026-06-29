import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.ai_engine import AIEngine


def test_vllm_provider_without_install():
    cfg = {"provider": "vllm", "model_path": ""}
    engine = AIEngine(cfg)
    # vllm not installed in test environment; engine should not crash
    resp = engine.chat("Hello", mode="chat", history=None)
    assert resp.startswith("[ERROR]") or isinstance(resp, str)

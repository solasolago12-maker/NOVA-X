import os
import sys

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.ai_engine import AIEngine


def test_detect_local_acceleration_returns_string():
    engine = AIEngine({"provider": "gemini"})
    res = engine._detect_local_acceleration()
    assert isinstance(res, str)
    assert res in ("cuda", "cpu")

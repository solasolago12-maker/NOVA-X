import os
import sys
import pytest

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.ai_engine import AIEngine


@pytest.mark.parametrize(
    "cfg, expected_host, expected_model",
    [
        ({"provider": "ollama", "host": "qwen2.5:7b", "model": "qwen2.5:7b"}, "", "qwen2.5:7b"),
        ({"provider": "ollama", "host": "http://localhost:11434/api/chat", "model": "qwen2.5:7b"}, "http://localhost:11434", "qwen2.5:7b"),
        ({"provider": "ollama", "host": "localhost:11434", "model": "qwen2.5:7b"}, "http://localhost:11434", "qwen2.5:7b"),
        ({"provider": "ollama", "host": "http://localhost:11434", "model": "qwen2.5:7b"}, "http://localhost:11434", "qwen2.5:7b"),
    ],
)
def test_ollama_host_normalization(cfg, expected_host, expected_model):
    engine = AIEngine(cfg)
    assert getattr(engine, "_host", None) == expected_host
    assert getattr(engine, "_model_name", None) == expected_model

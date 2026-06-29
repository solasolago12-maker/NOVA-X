import os
import sys

# Ensure project root is importable when running this script directly
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.ai_engine import AIEngine


def run_test_case(ai_config, desc):
    print("---", desc, "---")
    engine = AIEngine(ai_config)
    # Print internal host and model
    host = getattr(engine, "_host", None)
    model = getattr(engine, "_model_name", None)
    print(f"_host: {host!r}")
    print(f"_model_name: {model!r}")
    print()


if __name__ == "__main__":
    # Case 1: user provided a model-like string as host (should be rejected)
    cfg1 = {"provider": "ollama", "host": "qwen2.5:7b", "model": "qwen2.5:7b"}
    run_test_case(cfg1, "Model-like host (qwen2.5:7b)")

    # Case 2: user provided full API endpoint (should normalize to base host)
    cfg2 = {"provider": "ollama", "host": "http://localhost:11434/api/chat", "model": "qwen2.5:7b"}
    run_test_case(cfg2, "Full API endpoint (http://localhost:11434/api/chat)")

    # Case 3: user provided host:port (should be normalized to http://host:port)
    cfg3 = {"provider": "ollama", "host": "localhost:11434", "model": "qwen2.5:7b"}
    run_test_case(cfg3, "Host:port (localhost:11434)")

    # Case 4: valid http host without path
    cfg4 = {"provider": "ollama", "host": "http://localhost:11434", "model": "qwen2.5:7b"}
    run_test_case(cfg4, "Valid base URL (http://localhost:11434)")

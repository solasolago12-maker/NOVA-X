"""Auto-tune skill for NOVA-X.

This module exposes a simple skill wrapper around the existing local
benchmarking helpers. It is intended for skill-driven mode selection in
NOVA-X's TUI.
"""

from typing import List, Optional

from core.ai_engine import AIEngine
from examples.benchmark_local import run_benchmark


class AutoTuneSkill:
    """Auto-tune helper for local model performance."""

    def __init__(self, ai_engine: Optional[AIEngine] = None) -> None:
        self.ai = ai_engine

    def run(self, model_path: str, iterations: int = 3, warmup: int = 1) -> List[float]:
        """Run benchmarks for a local model and return measured durations."""
        return run_benchmark("local", model_path, iterations, warmup=warmup)

    def explain(self) -> str:
        """Return a short explanation for how to use the auto-tune skill."""
        return (
            "Auto-tune mode measures local model latency to find the best "
            "GPU configuration. Enter a model path and optional warmup/iteration "
            "parameters in the format: model_path=<path> iterations=<n> warmup=<n>."
        )

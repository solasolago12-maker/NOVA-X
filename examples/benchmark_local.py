#!/usr/bin/env python3
"""Benchmark local or vllm provider latency.

Usage:
    python examples/benchmark_local.py --provider local --model-path /path/to/model.gguf --iterations 10

The script performs a small number of warmup requests then measures average
latency for the configured provider using the NOVA-X `AIEngine`.
"""
import argparse
import time
from core.ai_engine import AIEngine


def run_benchmark(provider: str, model_path: str, iterations: int, warmup: int = 2):
    cfg = {"provider": provider}
    if provider == "local":
        cfg["model_path"] = model_path
    elif provider == "vllm":
        cfg["model_path"] = model_path

    engine = AIEngine(cfg)

    sample_prompt = "Write a short explanation of the Pythagorean theorem in 2-3 sentences."

    print(f"Provider: {provider}, model: {model_path}")
    print(f"Warming up with {warmup} runs...")
    for i in range(warmup):
        _ = engine.chat(sample_prompt, mode="chat", history=None)

    print(f"Running {iterations} timed iterations...")
    durations = []
    for i in range(iterations):
        t0 = time.perf_counter()
        _ = engine.chat(sample_prompt, mode="chat", history=None)
        t1 = time.perf_counter()
        dt = t1 - t0
        durations.append(dt)
        print(f"  iter {i+1}: {dt:.3f}s")

    avg = sum(durations) / len(durations) if durations else 0.0
    print(f"Average latency: {avg:.3f}s over {len(durations)} runs")


def main():
    parser = argparse.ArgumentParser(description="Benchmark local/vllm provider")
    parser.add_argument("--provider", choices=["local", "vllm"], default="local")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    args = parser.parse_args()

    run_benchmark(args.provider, args.model_path, args.iterations, warmup=args.warmup)


if __name__ == "__main__":
    main()

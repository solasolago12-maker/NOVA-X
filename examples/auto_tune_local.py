#!/usr/bin/env python3
"""Auto-tune `n_gpu_layers` for llama-cpp-python local provider.

This script runs a small benchmark for a set of candidate `n_gpu_layers`
values and writes the best-performing value to the NOVA-X config file
(`~/.nova_x/config.json`). It is best-effort: if no local model is
present the script will exit with an informative message.

Usage:
    python examples/auto_tune_local.py --model-path /path/to/model.gguf
"""
import argparse
import statistics
import tempfile
import os
from core.config_manager import ConfigManager
from examples.benchmark_local import run_benchmark

CANDIDATES = [0, 4, 8, 12, 16]


def auto_tune(model_path: str, iterations: int = 3, warmup: int = 1, csv_log: str | None = None, dry_run: bool = False):
    cfg_mgr = ConfigManager()

    best = None
    best_avg = None

    for candidate in CANDIDATES:
        print(f"Testing n_gpu_layers={candidate}...")
        # Temporarily set config values
        cfg_mgr.set("local_n_gpu_layers", candidate)
        try:
            durations = run_benchmark("local", model_path, iterations, warmup=warmup)
        except Exception as e:
            print(f"Benchmark failed for n_gpu_layers={candidate}: {e}")
            durations = []

        if not durations:
            print("No durations recorded; skipping candidate.")
            continue

        avg = statistics.mean(durations)
        print(f"n_gpu_layers={candidate} average {avg:.3f}s")
        if best_avg is None or avg < best_avg:
            best_avg = avg
            best = candidate

    if best is None:
        print("Auto-tune could not determine a best setting.")
        return

    print(f"Best n_gpu_layers: {best} (avg {best_avg:.3f}s).")
    if dry_run:
        print("Dry-run enabled; not persisting config or writing CSV.")
        return

    print("Persisting best setting to config.")
    cfg_mgr.set("local_n_gpu_layers", best)

    if csv_log:
        # Append a small note to CSV
        with open(csv_log, "a", encoding="utf-8") as fh:
            fh.write(f"auto_tune,{model_path},{best},{best_avg}\n")
        print(f"Logged auto-tune result to {csv_log}")


def main():
    parser = argparse.ArgumentParser(description="Auto-tune local model GPU layers")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--csv", help="CSV file to append results to", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Run auto-tune without persisting changes")
    args = parser.parse_args()

    auto_tune(args.model_path, iterations=args.iterations, warmup=args.warmup, csv_log=args.csv, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

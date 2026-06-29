#!/usr/bin/env python3
"""Example script: run a single local-model chat using the NOVA-X engine.

Usage:
    python examples/run_local.py --model-path /path/to/model.gguf
"""
import argparse
from core.ai_engine import AIEngine

parser = argparse.ArgumentParser(description="Run local model example")
parser.add_argument("--model-path", required=True, help="Path to local GGUF/GGML model file")
args = parser.parse_args()

cfg = {"provider": "local", "model_path": args.model_path}
engine = AIEngine(cfg)

print("Local model initialized. Type a message and press Enter (Ctrl+C to quit):")
try:
    while True:
        msg = input("You: ")
        if not msg:
            continue
        resp = engine.chat(msg, mode="chat", history=None)
        print("Assistant:", resp)
except KeyboardInterrupt:
    print("\nExiting.")

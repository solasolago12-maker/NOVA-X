#!/usr/bin/env python3
"""NOVA-X: Next-Gen Omniscient Virtual Assistant -- eXtreme

Main entry point for the NOVA-X AI homework assistant. Supports:
  --setup    Run the first-time setup wizard
  --mode     Launch directly into a specific mode

Usage:
    python nova_x.py
    python nova_x.py --setup
    python nova_x.py --mode math
"""

import argparse
import os
import re
import sys

# Ensure the project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.config_manager import ConfigManager


def _normalize_ollama_host(host: str) -> str:
    host = host.strip()
    if not host:
        return ""
    if host.startswith(("http://", "https://")):
        return host.rstrip("/")
    if re.match(r"^[\w\.-]+:\d+$", host):
        return f"http://{host}"
    return ""


def run_setup_wizard() -> None:
    """Interactive first-time setup wizard."""
    print("\n" + "=" * 60)
    print("   NOVA-X Setup Wizard")
    print("=" * 60 + "\n")

    config = ConfigManager()

    # Name
    name = input("What is your name? (optional): ").strip()
    if name:
        config.set("user_name", name)

    # Grade level
    print("\nGrade levels:")
    grades = ["Elementary (K-5)", "Middle School (6-8)", "High School (9-12)",
              "College / University", "Graduate", "Other"]
    for i, g in enumerate(grades, 1):
        print(f"  {i}. {g}")
    grade_choice = input("Select your grade level (1-6, or skip): ").strip()
    if grade_choice.isdigit() and 1 <= int(grade_choice) <= 6:
        config.set("grade_level", grades[int(grade_choice) - 1])

    # AI Provider
    print("\nAI Provider configuration:")
    print("  1. Gemini (Google) -- recommended")
    print("  2. Ollama (local)")
    print("  3. OpenAI / OpenAI-compatible")
    print("  4. Local (llama-cpp-python)")
    provider_choice = input("Select AI provider (1-4, default=1): ").strip() or "1"

    if provider_choice == "1":
        config.set("ai_provider", "gemini")
        api_key = input("Enter your Gemini API key: ").strip()
        if api_key:
            config.set("gemini_api_key", api_key)
    elif provider_choice == "2":
        config.set("ai_provider", "ollama")
        host = input("Ollama host (default: http://localhost:11434): ").strip()
        normalized_host = _normalize_ollama_host(host)
        if normalized_host:
            config.set("ollama_host", normalized_host)
        elif host:
            print("[WARNING] Invalid Ollama host. Expected http://host:port or host:port. Using default localhost:11434.")
        model = input("Ollama model (default: llama3.2, e.g. qwen2.5:7b): ").strip()
        if model:
            config.set("ollama_model", model)
    elif provider_choice == "3":
        config.set("ai_provider", "openai")
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            config.set("openai_api_key", api_key)
        base_url = input("Base URL (default: https://api.openai.com/v1): ").strip()
        if base_url:
            config.set("openai_base_url", base_url)
        model = input("Model (default: gpt-4o-mini): ").strip()
        if model:
            config.set("openai_model", model)
    elif provider_choice == "4":
        config.set("ai_provider", "local")
        model_path = input("Local model path (file or directory): ").strip()
        if model_path:
            config.set("local_model_path", model_path)

    # Subjects
    print("\nAdd subjects you want to track (comma-separated, or skip):")
    subjects_input = input("Subjects (e.g., Math, Physics, English): ").strip()
    if subjects_input:
        subjects = [s.strip() for s in subjects_input.split(",") if s.strip()]
        config.set("subjects", subjects)

    # Theme
    print("\nThemes: dark, light, neon, minimal")
    theme = input("Choose theme (default: dark): ").strip() or "dark"
    config.set("theme", theme)

    # Mark setup complete
    config.complete_first_run()

    print("\n" + "=" * 60)
    print("   Setup complete! Launch NOVA-X with: python nova_x.py")
    print("=" * 60 + "\n")


def launch_tui(start_mode: str = "chat") -> None:
    """Launch the full Rich-based TUI.

    Args:
        start_mode: Initial mode to activate.
    """
    try:
        from ui.screens import MainScreen
        screen = MainScreen()
        screen.run(start_mode=start_mode)
    except ImportError as exc:
        print(f"Failed to launch TUI: {exc}")
        print("Falling back to simple CLI...\n")
        run_simple_cli(start_mode)


def run_simple_cli(start_mode: str = "chat") -> None:
    """Fallback simple CLI without Rich dependency.

    Args:
        start_mode: Initial mode to activate.
    """
    from core.ai_engine import AIEngine
    from core.session import Session

    config = ConfigManager()
    ai_cfg = config.get_ai_config()
    ai = AIEngine(ai_cfg)
    session = Session(mode=start_mode)

    print("\n   NOVA-X -- Simple CLI Mode")
    print("   Type 'quit' to exit, 'help' for commands.\n")

    while True:
        try:
            mode_display = session.get_mode_display_name()
            user_input = input(f"[{mode_display}] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "/quit"):
                print("Goodbye!")
                break
            if user_input.lower() == "help":
                print("Commands: quit, help, mode <name>, clear")
                continue
            if user_input.lower().startswith("mode "):
                new_mode = user_input.split()[1]
                if session.set_mode(new_mode):
                    print(f"Switched to {session.get_mode_display_name()}")
                else:
                    print(f"Unknown mode: {new_mode}")
                continue
            if user_input.lower() == "clear":
                session.clear_history()
                print("History cleared.")
                continue

            print("NOVA-X is thinking...")
            response = ai.chat(user_input, mode=session.mode, history=session.get_history_for_ai())
            print(f"\n{response}\n")
            session.add_message("user", user_input)
            session.add_message("assistant", response)

        except KeyboardInterrupt:
            print("\nUse 'quit' to exit.")
        except EOFError:
            break


def main() -> None:
    """Parse arguments and launch the appropriate interface."""
    parser = argparse.ArgumentParser(
        description="NOVA-X: Next-Gen Omniscient Virtual Assistant -- eXtreme",
    )
    parser.add_argument(
        "--setup", action="store_true",
        help="Run the first-time setup wizard",
    )
    parser.add_argument(
        "--mode", type=str, default="chat",
        choices=["chat", "math", "essay", "code", "research", "quiz", "explain", "jarvis"],
        help="Launch directly into a specific mode (default: chat)",
    )
    parser.add_argument(
        "--auto-tune-local", action="store_true",
        help="Run auto-tune for local llama-cpp-python model (non-interactive).",
    )
    parser.add_argument(
        "--model-path", type=str, default="",
        help="Path to local model used by auto-tune/benchmark commands.",
    )
    parser.add_argument(
        "--iterations", type=int, default=3,
        help="Number of iterations for benchmarks/auto-tune (default: 3)",
    )
    parser.add_argument(
        "--warmup", type=int, default=1,
        help="Number of warmup runs for benchmarks (default: 1)",
    )
    parser.add_argument(
        "--csv", type=str, default="",
        help="Optional CSV file path to append benchmark results.",
    )
    args = parser.parse_args()

    if args.setup:
        run_setup_wizard()
        return

    if args.auto_tune_local:
        # Run auto-tune (non-interactive). Defer import to avoid heavy deps at startup.
        if not args.model_path:
            print("[ERROR] --model-path is required for --auto-tune-local")
            return
        try:
            from examples.auto_tune_local import auto_tune
            auto_tune(args.model_path, iterations=args.iterations, warmup=args.warmup, csv_log=args.csv or None)
        except Exception as exc:
            print(f"[ERROR] Auto-tune failed: {exc}")
        return

    config = ConfigManager()
    if config.is_first_run():
        print("\nWelcome to NOVA-X! It looks like this is your first time.")
        run_choice = input("Run setup wizard now? (Y/n): ").strip().lower()
        if run_choice in ("", "y", "yes"):
            run_setup_wizard()
            return

    launch_tui(start_mode=args.mode)


if __name__ == "__main__":
    main()

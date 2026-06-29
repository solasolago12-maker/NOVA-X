"""Main TUI screen for NOVA-X.

The :class:`MainScreen` class orchestrates the entire terminal UI:
initialising the Rich console, loading configuration, managing the AI
engine, handling user input, dispatching to mode-specific processors,
and rendering all output.
"""

import os
import re
import sys
import time
import uuid
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

# Core components
from core.config_manager import ConfigManager
from core.ai_engine import AIEngine
from core.session import Session, MODES
import re

# Memory components
from memory.profile import UserProfile
from memory.history import ConversationHistory
from memory.subjects import SubjectTracker

# Utility components
from utils.web_search import WebSearch
from utils.file_export import FileExporter
from utils.helpers import estimate_reading_time, progress_bar, safe_filename

# UI components
from ui.themes import THEMES
from ui import widgets

# Skill modules (assumed to exist in skills/ package)
try:
    from skills.math_solver import MathSolver
    from skills.essay_writer import EssayWriter
    from skills.code_helper import CodeHelper
    from skills.research import ResearchAssistant
    from skills.quiz_generator import QuizGenerator
    from skills.explainer import Explainer
    SKILLS_AVAILABLE = True
except ImportError:
    SKILLS_AVAILABLE = False


class MainScreen:
    """Main terminal UI controller for NOVA-X.

    Manages the full application lifecycle: setup, main input loop,
    mode dispatch, command handling, and graceful shutdown.
    """

    def __init__(self) -> None:
        """Initialise all subsystems."""
        self.config = ConfigManager()
        theme_name = self.config.get("theme", "dark")
        self.theme = THEMES.get(theme_name, THEMES["dark"])
        self.console = Console(theme=self.theme)

        # AI engine
        ai_cfg = self.config.get_ai_config()
        self.ai = AIEngine(ai_cfg)

        # Session
        self.session = Session()

        # Memory
        self.profile = UserProfile()
        self.history = ConversationHistory()
        self.subjects = SubjectTracker()

        # Utilities
        self.web_search = WebSearch()
        self.exporter = FileExporter()

        # Skills
        self.skills: Dict[str, Any] = {}
        if SKILLS_AVAILABLE:
            self.skills["math"] = MathSolver()
            self.skills["essay"] = EssayWriter()
            self.skills["code"] = CodeHelper()
            self.skills["research"] = ResearchAssistant()
            self.skills["quiz"] = QuizGenerator()
            self.skills["explain"] = Explainer()

        # State
        self._running = True
        self._last_response = ""

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self, start_mode: Optional[str] = None) -> None:
        """Run the main TUI loop.

        Args:
            start_mode: Optional mode to start in (e.g. ``math``).
        """
        if start_mode and start_mode in MODES:
            self.session.set_mode(start_mode)

        self.console.clear()
        self.console.print(widgets.create_welcome_screen(self.profile.name))

        while self._running:
            try:
                self._print_prompt()
                user_input = Prompt.ask("")
                user_input = user_input.strip()
                if not user_input:
                    continue
                self._process_input(user_input)
            except KeyboardInterrupt:
                self.console.print("\n[nova.warning]Use /quit to exit.[/nova.warning]")
            except EOFError:
                self._shutdown()

    def _print_prompt(self) -> None:
        """Print the mode-specific input prompt."""
        mode_display = self.session.get_mode_display_name()
        self.console.print(f"\n[nova.accent][{mode_display}][/nova.accent] ", end="")

    # ------------------------------------------------------------------
    # Input processing
    # ------------------------------------------------------------------

    def _process_input(self, user_input: str) -> None:
        """Dispatch user input to the appropriate handler."""
        # Commands
        if user_input.startswith("/"):
            self._handle_command(user_input)
            return

        # Mode-specific processing
        mode = self.session.mode
        if mode == "chat":
            self._process_chat(user_input)
        elif mode == "math":
            self._process_math(user_input)
        elif mode == "essay":
            self._process_essay(user_input)
        elif mode == "code":
            self._process_code(user_input)
        elif mode == "research":
            self._process_research(user_input)
        elif mode == "quiz":
            self._process_quiz(user_input)
        elif mode == "explain":
            self._process_explain(user_input)
        elif mode == "jarvis":
            self._process_jarvis(user_input)
        else:
            self._process_chat(user_input)

        # Track in history
        self.history.add_message("user", user_input)
        self.history.add_message("assistant", self._last_response)
        self.session.add_message("user", user_input)
        self.session.add_message("assistant", self._last_response)

    # ------------------------------------------------------------------
    # Chat mode
    # ------------------------------------------------------------------

    def _process_chat(self, message: str) -> None:
        """Process a general chat message."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()
        with self.console.status("[nova.info]NOVA-X is thinking...[/nova.info]", spinner="dots"):
            response = self.ai.chat(message, mode="default", history=self.session.get_history_for_ai())
        self._last_response = response
        self.console.print(Markdown(response))

    def _process_jarvis(self, message: str) -> None:
        """Process input in Jarvis command center mode."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()
        with self.console.status("[nova.info]Jarvis is analyzing...[/nova.info]", spinner="dots"):
            response = self.ai.chat(message, mode="jarvis", history=self.session.get_history_for_ai())
        self._last_response = response
        self.console.print(Markdown(response))

    # ------------------------------------------------------------------
    # Math mode
    # ------------------------------------------------------------------

    def _process_math(self, message: str) -> None:
        """Process math-related input."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()

        # Check for work-verification request
        if message.lower().startswith("check "):
            work = message[6:]
            if SKILLS_AVAILABLE and "math" in self.skills:
                result = self.skills["math"].check_work(work)
            else:
                with self.console.status("[nova.info]Checking your work...[/nova.info]"):
                    result = self.ai.chat(
                        f"Check this math work for errors. Point out any mistakes and explain the correct approach:\n\n{work}",
                        mode="math", history=self.session.get_history_for_ai(),
                    )
            self._last_response = result
            self.console.print(Panel(Markdown(result), title="Math Check", style="nova.border"))
            return

        # Solve
        if SKILLS_AVAILABLE and "math" in self.skills:
            with self.console.status("[nova.info]Solving...[/nova.info]"):
                result = self.skills["math"].solve(message)
        else:
            with self.console.status("[nova.info]Solving...[/nova.info]"):
                result = self.ai.chat(message, mode="math", history=self.session.get_history_for_ai())
        self._last_response = result
        self.console.print(Markdown(result))

    # ------------------------------------------------------------------
    # Essay mode
    # ------------------------------------------------------------------

    def _process_essay(self, message: str) -> None:
        """Process essay-writing input."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()

        cmd = message.lower().split()[0] if message.split() else ""
        rest = " ".join(message.split()[1:]) if len(message.split()) > 1 else ""

        if cmd == "outline" and rest:
            prompt = f"Create a detailed essay outline for: {rest}"
            with self.console.status("[nova.info]Generating outline...[/nova.info]"):
                result = self.ai.chat(prompt, mode="essay", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Panel(Markdown(result), title="Essay Outline", style="nova.border"))
        elif cmd == "draft" and rest:
            prompt = f"Write a complete essay draft based on this outline:\n\n{rest}"
            with self.console.status("[nova.info]Drafting essay...[/nova.info]"):
                result = self.ai.chat(prompt, mode="essay", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        elif cmd == "improve" and rest:
            prompt = f"Improve this essay. Fix grammar, clarity, structure, and style:\n\n{rest}"
            with self.console.status("[nova.info]Improving essay...[/nova.info]"):
                result = self.ai.chat(prompt, mode="essay", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        else:
            # General essay help
            with self.console.status("[nova.info]Thinking...[/nova.info]"):
                result = self.ai.chat(message, mode="essay", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))

    # ------------------------------------------------------------------
    # Code mode
    # ------------------------------------------------------------------

    def _process_code(self, message: str) -> None:
        """Process code-related input."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()

        cmd = message.lower().split()[0] if message.split() else ""
        rest = " ".join(message.split()[1:]) if len(message.split()) > 1 else ""

        if cmd == "write" and rest:
            prompt = f"Write clean, well-commented code for: {rest}"
            with self.console.status("[nova.info]Writing code...[/nova.info]"):
                result = self.ai.chat(prompt, mode="code", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        elif cmd == "debug" and rest:
            prompt = f"Debug this code. Identify issues and provide corrected version:\n\n```\n{rest}\n```"
            with self.console.status("[nova.info]Debugging...[/nova.info]"):
                result = self.ai.chat(prompt, mode="code", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        elif cmd == "explain" and rest:
            prompt = f"Explain this code step by step:\n\n```\n{rest}\n```"
            with self.console.status("[nova.info]Analyzing...[/nova.info]"):
                result = self.ai.chat(prompt, mode="code", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        elif cmd == "run" and rest:
            self._safe_execute_python(rest)
        else:
            with self.console.status("[nova.info]Thinking...[/nova.info]"):
                result = self.ai.chat(message, mode="code", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))

    def _safe_execute_python(self, code: str) -> None:
        """Execute Python code in a restricted environment."""
        import io
        import contextlib

        # Safety: block dangerous imports
        dangerous = ["os.system", "subprocess", "__import__", "eval", "exec",
                     "open(", "file(", "import os", "import sys",
                     "shutil", "pathlib.rmtree", "os.remove", "os.unlink"]
        for d in dangerous:
            if d in code.lower():
                self.console.print(Panel(
                    f"[nova.error]Blocked potentially unsafe code: '{d}'[/nova.error]",
                    title="Security", style="red"
                ))
                self._last_response = f"Execution blocked: unsafe pattern '{d}' detected."
                return

        self.console.print("[nova.info]Running Python code...[/nova.info]")
        output_buffer = io.StringIO()
        try:
            # Restricted globals
            safe_globals = {"__builtins__": __builtins__}
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                exec(compile(code, "<nova-x>", "exec"), safe_globals, {})
            output = output_buffer.getvalue()
            if not output.strip():
                output = "(Code executed successfully with no output)"
            self.console.print(Panel(output, title="Output", style="green"))
            self._last_response = f"Output:\n{output}"
        except Exception as exc:
            error_msg = f"{type(exc).__name__}: {exc}"
            self.console.print(Panel(f"[nova.error]{error_msg}[/nova.error]", title="Error", style="red"))
            self._last_response = f"Error: {error_msg}"

    # ------------------------------------------------------------------
    # Research mode
    # ------------------------------------------------------------------

    def _process_research(self, message: str) -> None:
        """Process research-related input."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()

        cmd = message.lower().split()[0] if message.split() else ""
        rest = " ".join(message.split()[1:]) if len(message.split()) > 1 else ""

        if cmd == "search" and rest:
            self.console.print(f"[nova.info]Searching the web for: {rest}...[/nova.info]")
            results = self.web_search.search(rest, num_results=5)
            if results:
                output_lines = [f'## Search Results for "{rest}"\n']
                for i, r in enumerate(results, 1):
                    output_lines.append(f"### {i}. {r.title}")
                    output_lines.append(f"{r.url}")
                    output_lines.append(f"{r.snippet}\n")
                result_text = "\n".join(output_lines)
                self.console.print(Markdown(result_text))
                self._last_response = result_text
            else:
                msg = "No web search results found."
                self.console.print(f"[nova.warning]{msg}[/nova.warning]")
                self._last_response = msg
        elif cmd == "deep" and rest:
            self.console.print(f"[nova.info]Conducting deep research on: {rest}...[/nova.info]")
            search_results = self.web_search.search(rest, num_results=5)
            context = "\n".join([f"- {r.title}: {r.snippet}" for r in search_results])
            prompt = f'Research the topic "{rest}" thoroughly. Use the following search results as context:\n\n{context}\n\nProvide a comprehensive, well-structured summary with key findings, important facts, and further reading suggestions.'
            with self.console.status("[nova.info]Synthesizing research...[/nova.info]"):
                result = self.ai.chat(prompt, mode="research", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))
        else:
            with self.console.status("[nova.info]Researching...[/nova.info]"):
                result = self.ai.chat(message, mode="research", history=self.session.get_history_for_ai())
            self._last_response = result
            self.console.print(Markdown(result))

    # ------------------------------------------------------------------
    # Quiz mode
    # ------------------------------------------------------------------

    def _process_quiz(self, message: str) -> None:
        """Generate and administer a quiz."""
        self.console.print(widgets.create_chat_message("user", message))

        cmd = message.lower().split()[0] if message.split() else ""
        subject = " ".join(message.split()[1:]) if len(message.split()) > 1 else "General"

        # Generate quiz
        self.console.print(f"[nova.info]Generating a quiz on: {subject}...[/nova.info]")
        prompt = (
            f"Generate a 5-question multiple-choice quiz about {subject}. "
            f"Format each question as:\n"
            f"Q1. [Question text]\n"
            f"A) [Option] B) [Option] C) [Option] D) [Option]\n"
            f"\nAfter all questions, provide an answer key in the format:\n"
            f"ANSWERS: Q1:A, Q2:B, Q3:C, Q4:D, Q5:A"
        )
        with self.console.status("[nova.info]Creating quiz...[/nova.info]"):
            quiz_text = self.ai.chat(prompt, mode="quiz", history=self.session.get_history_for_ai())

        self._last_response = quiz_text
        self.console.print(Panel(Markdown(quiz_text), title=f"Quiz: {subject}", style="nova.border"))

        # Extract answers and administer
        answers_match = re.search(r"ANSWERS:\s*([Q\d:A-D,\s]+)", quiz_text, re.IGNORECASE)
        if answers_match:
            answers_str = answers_match.group(1)
            answers = {}
            for part in re.findall(r"Q(\d+):([A-D])", answers_str, re.IGNORECASE):
                answers[int(part[0])] = part[1].upper()

            score = 0
            total = len(answers)
            if total > 0:
                self.console.print("\n[nova.accent]--- Answer the questions below ---[/nova.accent]\n")
                for q_num in sorted(answers.keys()):
                    user_ans = Prompt.ask(f"Your answer for Q{q_num} (A/B/C/D)").strip().upper()
                    correct = answers[q_num]
                    if user_ans == correct:
                        self.console.print(f"  [nova.success]Correct![/nova.success]")
                        score += 1
                    else:
                        self.console.print(f"  [nova.error]Wrong. Correct answer: {correct}[/nova.error]")

                pct = (score / total) * 100
                self.console.print(f"\n[nova.accent]Score: {score}/{total} ({pct:.0f}%)[/nova.accent]")
                self.profile.record_quiz_result(subject, score, total)
                self._last_response += f"\n\nUser scored {score}/{total} ({pct:.0f}%)"

    # ------------------------------------------------------------------
    # Explain mode
    # ------------------------------------------------------------------

    def _process_explain(self, message: str) -> None:
        """Process explanation-related input."""
        self.console.print(widgets.create_chat_message("user", message))
        self.console.print()

        cmd = message.lower().split()[0] if message.split() else ""
        rest = " ".join(message.split()[1:]) if len(message.split()) > 1 else ""

        if cmd == "analogy" and rest:
            prompt = f'Explain "{rest}" using a simple, relatable analogy that a student would understand.'
        elif cmd == "summarize" and rest:
            prompt = f"Summarize the following text concisely, highlighting the key points:\n\n{rest}"
        elif cmd == "mindmap" and rest:
            prompt = f'Create a text-based mind map outline for "{rest}". Use indentation and bullet points to show hierarchy and relationships.'
        elif cmd == "terms" and rest:
            prompt = f'Define the key terms and vocabulary related to "{rest}". Provide simple definitions suitable for a student.'
        else:
            prompt = message

        with self.console.status("[nova.info]Explaining...[/nova.info]"):
            result = self.ai.chat(prompt, mode="explain", history=self.session.get_history_for_ai())
        self._last_response = result
        self.console.print(Markdown(result))

    # ------------------------------------------------------------------
    # Command handling
    # ------------------------------------------------------------------

    def _handle_command(self, command: str) -> None:
        """Process slash commands."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("/quit", "/exit"):
            self._shutdown()
        elif cmd == "/help":
            self.console.print(widgets.create_help_screen())
        elif cmd == "/mode":
            if args:
                new_mode = args[0].lower()
                if self.session.set_mode(new_mode):
                    self.console.print(f"[nova.success]Switched to {self.session.get_mode_display_name()} mode.[/nova.success]")
                else:
                    self.console.print(f"[nova.error]Unknown mode: {new_mode}. Available: {', '.join(MODES)}[/nova.error]")
            else:
                self.console.print(f"[nova.info]Current mode: {self.session.get_mode_display_name()}. Available: {', '.join(MODES)}[/nova.info]")
        elif cmd == "/clear":
            self.session.clear_history()
            self.history.clear_current()
            self.console.clear()
            self.console.print("[nova.success]Conversation cleared.[/nova.success]")
        elif cmd == "/save":
            fmt = args[0] if args else "txt"
            self._save_chat(fmt)
        elif cmd == "/history":
            self._show_history()
        elif cmd == "/subjects":
            self._handle_subjects(args)
        elif cmd == "/assignments":
            self._show_assignments()
        elif cmd == "/quiz":
            if args:
                self._process_quiz("start " + " ".join(args))
            else:
                self.console.print("[nova.warning]Usage: /quiz <subject>[/nova.warning]")
        elif cmd == "/explain":
            if args:
                self._process_explain("analogy " + " ".join(args))
            else:
                self.console.print("[nova.warning]Usage: /explain <topic>[/nova.warning]")
        elif cmd == "/provider":
            self._handle_provider(args)
        elif cmd == "/host":
            provider = self.config.get("ai_provider")
            if provider == "ollama":
                host = self.config.get("ollama_host", "http://localhost:11434")
            elif provider == "openai":
                host = self.config.get("openai_base_url", "https://api.openai.com/v1")
            else:
                host = "N/A"
            self.console.print(f"[nova.info]Current host/endpoint for {provider}: {host}[/nova.info]")
        elif cmd == "/status":
            self.console.print(widgets.create_status_panel(
                provider=self.config.get("ai_provider"),
                model=self.config.get("ollama_model") if self.config.get("ai_provider") == "ollama" else self.config.get("openai_model") if self.config.get("ai_provider") == "openai" else self.config.get("gemini_model"),
                mode=self.session.get_mode_display_name(),
                theme=self.config.get("theme", "dark"),
                user=self.profile.name or "Student",
            ))
        elif cmd == "/stats":
            stats = self.profile.get_stats()
            self.console.print(widgets.create_stats_panel(stats))
        elif cmd == "/welcome":
            self.console.print(widgets.create_welcome_screen(self.profile.name))
        else:
            self.console.print(f"[nova.error]Unknown command: {cmd}. Type /help for available commands.[/nova.error]")

    def _handle_provider(self, args: List[str]) -> None:
        """Manage AI provider configuration at runtime."""
        if not args:
            provider = self.config.get("ai_provider")
            model = self.config.get("ollama_model") if provider == "ollama" else self.config.get("openai_model") if provider == "openai" else self.config.get("gemini_model")
            self.console.print(
                f"[nova.info]Current provider: {provider}, model: {model}[/nova.info]"
            )
            return

        action = args[0].lower()
        if action == "info":
            provider = self.config.get("ai_provider")
            model = self.config.get("ollama_model") if provider == "ollama" else self.config.get("openai_model") if provider == "openai" else self.config.get("gemini_model")
            host = self.config.get("ollama_host", "http://localhost:11434") if provider == "ollama" else self.config.get("openai_base_url", "https://api.openai.com/v1") if provider == "openai" else "N/A"
            self.console.print(f"[nova.info]Provider: {provider} | Model: {model} | Host/Endpoint: {host}[/nova.info]")
            return
        if action == "validate":
            provider = self.config.get("ai_provider")
            if provider == "ollama":
                host = self.config.get("ollama_host", "")
                model = self.config.get("ollama_model", "")
                valid_host = AIEngine._is_valid_ollama_host(host)
                self.console.print(f"[nova.info]Ollama host valid: {valid_host} | Host: {host} | Model: {model}[/nova.info]")
                if not valid_host:
                    self.console.print("[nova.error]Invalid Ollama host. Use http://host:port or host:port format.[/nova.error]")
            elif provider == "openai":
                base_url = self.config.get("openai_base_url", "")
                model = self.config.get("openai_model", "")
                valid_base = base_url.startswith(("http://", "https://"))
                self.console.print(f"[nova.info]OpenAI base URL valid: {valid_base} | Base URL: {base_url} | Model: {model}[/nova.info]")
                if not valid_base:
                    self.console.print("[nova.error]Invalid OpenAI base URL. Use a valid HTTP or HTTPS endpoint.[/nova.error]")
            else:
                api_key = self.config.get("gemini_api_key", "")
                model = self.config.get("gemini_model", "")
                self.console.print(f"[nova.info]Gemini API key configured: {bool(api_key)} | Model: {model}[/nova.info]")
            return
        if action == "list":
            self.console.print("[nova.info]Available providers: gemini, ollama, openai[/nova.info]")
            return
        if action == "models":
            models = self.ai.get_available_models()
            self.console.print(f"[nova.info]Available models for {self.config.get('ai_provider')}: {', '.join(models)}[/nova.info]")
            return
        if action == "set" and len(args) >= 2:
            provider = args[1].lower()
            if provider not in ("gemini", "ollama", "openai"):
                self.console.print("[nova.error]Invalid provider. Choose gemini, ollama, or openai.[/nova.error]")
                return

            host = None
            model = None
            for extra in args[2:]:
                if extra.startswith("host="):
                    host = extra.split("=", 1)[1]
                elif extra.startswith("model="):
                    model = extra.split("=", 1)[1]
                elif provider == "ollama" and (extra.startswith(("http://", "https://")) or re.match(r"^[\w\.-]+:\d+$", extra)):
                    host = extra
                else:
                    model = extra

            self.config.set("ai_provider", provider)
            if provider == "gemini":
                if model:
                    self.config.set("gemini_model", model)
                ai_cfg = self.config.get_ai_config()
                self.ai.set_provider("gemini", **ai_cfg)
                display_model = self.config.get("gemini_model")
            elif provider == "ollama":
                if host and not AIEngine._is_valid_ollama_host(host):
                    self.console.print("[nova.error]Invalid Ollama host. Use http://host:port or host:port format.[/nova.error]")
                    return
                if host:
                    self.config.set("ollama_host", host)
                if model:
                    self.config.set("ollama_model", model)
                ai_cfg = self.config.get_ai_config()
                self.ai.set_provider("ollama", **ai_cfg)
                display_model = self.config.get("ollama_model")
            else:
                if model:
                    self.config.set("openai_model", model)
                ai_cfg = self.config.get_ai_config()
                self.ai.set_provider("openai", **ai_cfg)
                display_model = self.config.get("openai_model")

            self.console.print(f"[nova.success]Provider set to {provider} with model {display_model}.[/nova.success]")
            if provider == "ollama" and not self.config.get("ollama_host", "").startswith(("http://", "https://")):
                self.console.print("[nova.warning]Warning: Ollama host should be a valid URL like http://localhost:11434[/nova.warning]")
            return

        self.console.print("[nova.warning]Usage: /provider [list|models|set <provider> [host=<url>] [model=<name>]][/nova.warning]")

    def _save_chat(self, fmt: str) -> None:
        """Export the current conversation."""
        content_lines = []
        for msg in self.session.history:
            role = msg["role"].capitalize()
            content_lines.append(f"## {role}\n\n{msg['content']}\n")
        content = "\n".join(content_lines)
        filename = f"nova_x_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            if fmt == "md":
                path = self.exporter.export_md(content, filename=filename)
            elif fmt == "docx":
                path = self.exporter.export_docx(content, filename=filename)
            elif fmt == "pdf":
                path = self.exporter.export_pdf(content, filename=filename)
            else:
                path = self.exporter.export_txt(content, filename=filename)
            self.console.print(f"[nova.success]Chat saved to: {path}[/nova.success]")
        except Exception as exc:
            self.console.print(f"[nova.error]Save failed: {exc}[/nova.error]")

    def _show_history(self) -> None:
        """Display past sessions."""
        sessions = self.history.list_sessions(limit=10)
        if not sessions:
            self.console.print("[nova.info]No saved sessions found.[/nova.info]")
            return
        self.console.print("\n[nova.accent]Recent Sessions:[/nova.accent]\n")
        for s in sessions:
            self.console.print(f"  {s['date'][:19]} | {s['mode']:15} | {s['message_count']} messages", style="nova.main")

    def _handle_subjects(self, args: List[str]) -> None:
        """Handle subject management commands."""
        if not args:
            subjects = self.subjects.get_subjects()
            self.console.print("\n[nova.accent]Tracked Subjects:[/nova.accent]\n")
            if subjects:
                for name, info in subjects.items():
                    desc = info.get("description", "")
                    self.console.print(f"  • {name} {f'({desc})' if desc else ''}", style="nova.info")
            else:
                self.console.print("  (No subjects tracked)", style="nova.warning")
                self.console.print("  Usage: /subjects add <name>", style="nova.main")
        elif args[0] == "add" and len(args) > 1:
            self.subjects.add_subject(" ".join(args[1:]))
            self.console.print(f"[nova.success]Added subject: {' '.join(args[1:])}[/nova.success]")
        elif args[0] == "remove" and len(args) > 1:
            if self.subjects.remove_subject(" ".join(args[1:])):
                self.console.print(f"[nova.success]Removed subject.[/nova.success]")
            else:
                self.console.print(f"[nova.error]Subject not found.[/nova.error]")
        else:
            self.console.print("[nova.warning]Usage: /subjects [add|remove] <name>[/nova.warning]")

    def _show_assignments(self) -> None:
        """Display upcoming and overdue assignments."""
        upcoming = self.subjects.get_upcoming(days=14)
        overdue = self.subjects.get_overdue()
        all_assignments = overdue + upcoming
        self.console.print(widgets.create_assignments_panel(all_assignments))

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def _shutdown(self) -> None:
        """Gracefully shut down the application."""
        self._running = False
        # Save session
        if self.session.history:
            self.history.current_session = list(self.session.history)
            saved_path = self.history.save_session(mode=self.session.mode)
            self.console.print(f"[nova.info]Session saved to: {saved_path}[/nova.info]")
        self.profile.record_session(len(self.session.history))
        self.console.print("\n[nova.success]Goodbye! Keep learning![/nova.success]\n")

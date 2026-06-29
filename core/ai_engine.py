"""AI Engine for NOVA-X.

Provides a unified interface to multiple AI providers:
* **Gemini** – Google Generative AI (default)
* **Ollama** – Local LLM via HTTP
* **OpenAI** – OpenAI-compatible APIs

Both synchronous (:meth:`chat`) and streaming (:meth:`chat_stream`) interfaces
are supported.  The engine loads provider credentials from the user's
configuration and dispatches requests accordingly.
"""

import json
import os
import re
from typing import Any, Dict, Iterator, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import requests


# ---------------------------------------------------------------------------
# System prompts tailored for each mode
# ---------------------------------------------------------------------------

SYSTEM_PROMPTS: Dict[str, str] = {
    "default": (
        "You are NOVA-X, an advanced virtual assistant and expert tutor. You are confident, "
        "precise, and proactive. Provide clear, structured answers, anticipate follow-up "
        "questions, and explain your reasoning. Use markdown formatting for readability."
    ),
    "jarvis": (
        "You are NOVA-X in Jarvis mode. Act as a powerful, responsive command assistant. "
        "Offer concise guidance, execute strategy-style reasoning, and surface the most "
        "important details. Keep responses focused, authoritative, and easy to act on."
    ),
    "math": (
        "You are NOVA-X in Math mode. Solve problems step-by-step with crisp, logical "
        "explanations. Verify each result and make the reasoning easy to follow. Use "
        "LaTeX-style formatting for equations and support algebra, calculus, geometry, "
        "statistics, and advanced problem solving."
    ),
    "essay": (
        "You are NOVA-X in Essay mode. Help students write strong, polished essays. "
        "Produce clear outlines, compelling thesis statements, and well-organized prose. "
        "Improve style, tone, clarity, and structure while preserving the student's voice."
    ),
    "code": (
        "You are NOVA-X in Code mode. Help with programming problems and software design. "
        "Write clean, maintainable code and explain algorithms, data structures, and edge "
        "cases. Debug issues efficiently and provide optimized solutions for Python, "
        "JavaScript, Java, C++, and other languages."
    ),
    "research": (
        "You are NOVA-X in Research mode. Gather and synthesize information with depth "
        "and clarity. Provide summaries, key findings, source evaluations, and next-step "
        "recommendations. Present balanced perspectives and highlight the most relevant facts."
    ),
    "quiz": (
        "You are NOVA-X in Quiz mode. Generate engaging quizzes with multiple choice, "
        "true/false, and short-answer questions. Provide immediate explanations, adapt "
        "difficulty, and help students learn from mistakes."
    ),
    "explain": (
        "You are NOVA-X in Explain mode. Break down complex concepts into clear, vivid "
        "explanations. Use analogies, examples, and mental models. Tailor the response to "
        "the user's level and make the ideas intuitive and memorable."
    ),
}


class AIEngine:
    """Unified AI engine supporting multiple backend providers.

    The engine is configured via a dictionary (usually produced by
    :meth:`ConfigManager.get_ai_config`).  It initialises the correct
    provider client on first use and exposes a single ``chat`` interface
    regardless of the backend.

    Args:
        ai_config: Provider configuration mapping.
    """

    def __init__(self, ai_config: Optional[Dict[str, str]] = None) -> None:
        self._config = ai_config or {}
        self._provider = self._config.get("provider", "gemini")
        self._model_client: Any = None
        self._init_provider()

    # ------------------------------------------------------------------
    # Provider initialisation
    # ------------------------------------------------------------------

    def _init_provider(self) -> None:
        """Initialise the selected AI provider client."""
        if self._provider == "gemini":
            self._init_gemini()
        elif self._provider == "ollama":
            self._init_ollama()
        elif self._provider == "openai":
            self._init_openai()

    @staticmethod
    def _is_valid_ollama_host(host: str) -> bool:
        """Return True when the Ollama host is a valid URL or host:port string."""
        host = str(host or "").strip()
        if not host:
            return False
        if host.startswith(("http://", "https://")):
            return True
        return bool(re.match(r"^[\w\.-]+:\d+$", host))

    def _init_gemini(self) -> None:
        """Set up the Google Gemini API client."""
        try:
            import google.generativeai as genai
            api_key = self._config.get("api_key", "")
            if api_key:
                genai.configure(api_key=api_key)
            self._model_client = genai.GenerativeModel(
                self._config.get("model", "gemini-2.0-flash")
            )
        except ImportError:
            print("[WARNING] google-generativeai not installed. Gemini unavailable.")
            self._model_client = None

    def _init_ollama(self) -> None:
        """Set up the Ollama local LLM connection."""
        raw_host = str(self._config.get("host", "http://localhost:11434")).strip()
        if raw_host.startswith(("http://", "https://")):
            parsed = urlparse(raw_host)
            self._host = urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
        elif re.match(r"^[\w\.-]+:\d+$", raw_host):
            self._host = f"http://{raw_host}"
        elif raw_host:
            self._host = ""
        else:
            self._host = "http://localhost:11434"
        self._model_name = self._config.get("model", "llama3.2")
        self._model_client = "ollama"  # Ollama uses direct HTTP calls

    def _init_openai(self) -> None:
        """Set up the OpenAI-compatible API connection."""
        self._base_url = self._config.get("base_url", "https://api.openai.com/v1")
        self._api_key = self._config.get("api_key", "")
        self._model_name = self._config.get("model", "gpt-4o-mini")
        self._model_client = "openai"

    # ------------------------------------------------------------------
    # Provider switching
    # ------------------------------------------------------------------

    def set_provider(self, provider: str, **kwargs: str) -> None:
        """Switch to a different AI provider at runtime.

        Args:
            provider: One of ``gemini``, ``ollama``, or ``openai``.
            **kwargs: Provider-specific settings (e.g. ``api_key``, ``host``).
        """
        self._provider = provider
        self._config.update(kwargs)
        self._init_provider()

    def get_available_models(self) -> List[str]:
        """Return a list of model names available for the current provider.

        Returns:
            List of model identifier strings.
        """
        if self._provider == "gemini":
            return ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro"]
        elif self._provider == "ollama":
            try:
                resp = requests.get(f"{self._host}/api/tags", timeout=5)
                if resp.status_code == 200:
                    return [m["name"] for m in resp.json().get("models", [])]
            except requests.RequestException:
                pass
            return ["llama3.2", "llama3.1", "mistral", "phi4", "qwen2.5", "qwen2.5:7b"]
        elif self._provider == "openai":
            return ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        return []

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, mode: str = "default", history: Optional[List[Dict[str, str]]] = None) -> str:
        """Send a chat message and return the complete response.

        Args:
            message: The user\'s message text.
            mode: Operation mode key (e.g. ``math``, ``essay``).
            history: Optional conversation history as a list of dicts with
                ``role`` and ``content`` keys.

        Returns:
            The AI\'s response text.
        """
        if self._provider == "gemini":
            return self._chat_gemini(message, mode, history)
        elif self._provider == "ollama":
            return self._chat_ollama(message, mode, history)
        elif self._provider == "openai":
            return self._chat_openai(message, mode, history)
        return "[ERROR] No AI provider configured."

    def chat_stream(self, message: str, mode: str = "default", history: Optional[List[Dict[str, str]]] = None) -> Iterator[str]:
        """Send a chat message and yield response chunks as they arrive.

        Args:
            message: The user\'s message text.
            mode: Operation mode key.
            history: Optional conversation history.

        Yields:
            Text chunks from the AI response.
        """
        if self._provider == "gemini":
            yield from self._chat_gemini_stream(message, mode, history)
        elif self._provider == "ollama":
            yield from self._chat_ollama_stream(message, mode, history)
        elif self._provider == "openai":
            yield from self._chat_openai_stream(message, mode, history)
        else:
            yield "[ERROR] No AI provider configured."

    # ------------------------------------------------------------------
    # Gemini provider
    # ------------------------------------------------------------------

    def _chat_gemini(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Synchronous Gemini chat."""
        if self._model_client is None:
            return "[ERROR] Gemini client not initialised. Install google-generativeai and configure API key."
        try:
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            chat = self._model_client.start_chat(history=[])
            # Send system context as first message
            chat.send_message(system)
            # Add history
            if history:
                for msg in history[-10:]:
                    if msg.get("role") == "user":
                        chat.send_message(msg["content"])
            response = chat.send_message(message)
            return response.text
        except Exception as exc:
            return f"[ERROR] Gemini request failed: {exc}"

    def _chat_gemini_stream(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> Iterator[str]:
        """Streaming Gemini chat."""
        if self._model_client is None:
            yield "[ERROR] Gemini client not initialised."
            return
        try:
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            chat = self._model_client.start_chat(history=[])
            chat.send_message(system)
            if history:
                for msg in history[-10:]:
                    if msg.get("role") == "user":
                        chat.send_message(msg["content"])
            for chunk in chat.send_message(message, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            yield f"[ERROR] Gemini streaming failed: {exc}"

    # ------------------------------------------------------------------
    # Ollama provider
    # ------------------------------------------------------------------

    def _chat_ollama(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Synchronous Ollama chat."""
        try:
            if not self._is_valid_ollama_host(self._host):
                return "[ERROR] Invalid Ollama host configured. Use a valid URL like http://localhost:11434 or host:port format."
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
            if history:
                messages.extend([{"role": m["role"], "content": m["content"]} for m in history[-10:]])
            messages.append({"role": "user", "content": message})
            resp = requests.post(
                f"{self._host}/api/chat",
                json={"model": self._model_name, "messages": messages, "stream": False},
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content", "[No response]")
            return f"[ERROR] Ollama returned {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            return f"[ERROR] Ollama request failed: {exc}"

    def _chat_ollama_stream(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> Iterator[str]:
        """Streaming Ollama chat."""
        try:
            if not self._is_valid_ollama_host(self._host):
                yield "[ERROR] Invalid Ollama host configured. Use a valid URL like http://localhost:11434 or host:port format."
                return
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
            if history:
                messages.extend([{"role": m["role"], "content": m["content"]} for m in history[-10:]])
            messages.append({"role": "user", "content": message})
            resp = requests.post(
                f"{self._host}/api/chat",
                json={"model": self._model_name, "messages": messages, "stream": True},
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
        except requests.RequestException as exc:
            yield f"[ERROR] Ollama streaming failed: {exc}"

    # ------------------------------------------------------------------
    # OpenAI provider
    # ------------------------------------------------------------------

    def _chat_openai(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> str:
        """Synchronous OpenAI-compatible chat."""
        try:
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
            if history:
                messages.extend([{"role": m["role"], "content": m["content"]} for m in history[-10:]])
            messages.append({"role": "user", "content": message})
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json={"model": self._model_name, "messages": messages, "stream": False},
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"].get("content", "[No response]")
            return f"[ERROR] OpenAI API returned {resp.status_code}: {resp.text[:200]}"
        except requests.RequestException as exc:
            return f"[ERROR] OpenAI request failed: {exc}"

    def _chat_openai_stream(self, message: str, mode: str, history: Optional[List[Dict[str, str]]]) -> Iterator[str]:
        """Streaming OpenAI-compatible chat."""
        try:
            system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["default"])
            messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
            if history:
                messages.extend([{"role": m["role"], "content": m["content"]} for m in history[-10:]])
            messages.append({"role": "user", "content": message})
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
            resp = requests.post(
                f"{self._base_url}/chat/completions",
                headers=headers,
                json={"model": self._model_name, "messages": messages, "stream": True},
                stream=True,
                timeout=120,
            )
            for line in resp.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        line = line[6:]
                    if line == "[DONE]":
                        break
                    try:
                        data = json.loads(line)
                        delta = data["choices"][0].get("delta", {})
                        chunk = delta.get("content", "")
                        if chunk:
                            yield chunk
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except requests.RequestException as exc:
            yield f"[ERROR] OpenAI streaming failed: {exc}"

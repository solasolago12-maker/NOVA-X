"""Configuration manager for NOVA-X.

Handles loading, saving, and accessing user configuration stored in
~/.nova_x/config.json. Supports multiple AI providers, theming, and
user preferences.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG: Dict[str, Any] = {
    "ai_provider": "gemini",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.0-flash",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "llama3.2",
    "openai_api_key": "",
    "openai_base_url": "https://api.openai.com/v1",
    "openai_model": "gpt-4o-mini",
    "local_model_path": "",
    "local_n_ctx": 2048,
    "local_n_gpu_layers": 0,
    "local_use_mmap": True,
    "vllm_model_path": "",
    "theme": "dark",
    "user_name": "",
    "grade_level": "",
    "subjects": [],
    "first_run": True,
}


class ConfigManager:
    """Manages NOVA-X configuration persistence and access.

    Configuration is stored as JSON in ``~/.nova_x/config.json``. The manager
    provides a dictionary-like interface with dot-style convenience accessors
    and ensures that default values always exist.

    Example:
        >>> cfg = ConfigManager()
        >>> cfg.get("ai_provider")
        "gemini"
        >>> cfg.set("user_name", "Alice")
        >>> cfg.save()
    """

    def __init__(self) -> None:
        """Initialise the manager and load existing configuration."""
        self._config_dir = Path.home() / ".nova_x"
        self._config_path = self._config_dir / "config.json"
        self._config: Dict[str, Any] = {}
        self._ensure_config()
        self.load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_config(self) -> None:
        """Ensure the configuration directory and file exist.

        If the directory or file are missing, they are created with the
        default configuration values.
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)
        if not self._config_path.exists():
            self._config = dict(DEFAULT_CONFIG)
            self.save()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load configuration from disk, merging with defaults.

        Missing keys are back-filled from :data:`DEFAULT_CONFIG` so that
        upgrades do not break existing user configurations.
        """
        try:
            with open(self._config_path, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            merged = dict(DEFAULT_CONFIG)
            merged.update(loaded)
            self._config = merged
        except (json.JSONDecodeError, OSError):
            self._config = dict(DEFAULT_CONFIG)
            self.save()

    def save(self) -> None:
        """Persist current configuration to disk."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as fh:
                json.dump(self._config, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"[ERROR] Failed to save config: {exc}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a configuration value.

        Args:
            key: The configuration key.
            default: Value returned if *key* is absent.

        Returns:
            The stored value or *default*.
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and persist immediately.

        Args:
            key: The configuration key.
            value: The value to store.
        """
        self._config[key] = value
        self.save()

    def is_first_run(self) -> bool:
        """Return ``True`` if the application has never been configured."""
        return bool(self._config.get("first_run", True))

    def complete_first_run(self) -> None:
        """Mark the initial setup as completed."""
        self.set("first_run", False)

    def get_ai_config(self) -> Dict[str, str]:
        """Return a dictionary with AI provider-specific settings.

        The returned dictionary contains the keys required by the currently
        selected provider (e.g. ``api_key``, ``model``, ``base_url``).

        Returns:
            Provider configuration mapping.
        """
        provider = self._config.get("ai_provider", "gemini")
        if provider == "gemini":
            return {
                "provider": "gemini",
                "api_key": self._config.get("gemini_api_key", ""),
                "model": self._config.get("gemini_model", "gemini-2.0-flash"),
            }
        elif provider == "ollama":
            return {
                "provider": "ollama",
                "host": self._config.get("ollama_host", "http://localhost:11434"),
                "model": self._config.get("ollama_model", "llama3.2"),
            }
        elif provider == "openai":
            return {
                "provider": "openai",
                "api_key": self._config.get("openai_api_key", ""),
                "base_url": self._config.get("openai_base_url", "https://api.openai.com/v1"),
                "model": self._config.get("openai_model", "gpt-4o-mini"),
            }
        elif provider == "local":
            return {
                "provider": "local",
                "model_path": self._config.get("local_model_path", ""),
                "n_ctx": self._config.get("local_n_ctx", 2048),
                "n_gpu_layers": self._config.get("local_n_gpu_layers", 0),
                "use_mmap": self._config.get("local_use_mmap", True),
            }
        elif provider == "vllm":
            return {
                "provider": "vllm",
                "model_path": self._config.get("vllm_model_path", ""),
            }
        return {"provider": provider}

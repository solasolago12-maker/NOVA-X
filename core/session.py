"""Session management for NOVA-X.

A :class:`Session` represents a single user interaction session. It tracks the
active mode, conversation history, metadata context, and usage statistics.
Sessions can be serialised to dictionaries for persistence.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


MODES = ["chat", "math", "essay", "code", "research", "quiz", "explain", "auto_tune", "jarvis"]

MODE_DISPLAY_NAMES: Dict[str, str] = {
    "chat": "General Chat",
    "math": "Math Solver",
    "essay": "Essay Writer",
    "code": "Code Helper",
    "research": "Research Assistant",
    "quiz": "Quiz Generator",
    "explain": "Explainer",
    "auto_tune": "Auto-Tune",
    "jarvis": "Jarvis Command Center",
}


class Session:
    """A single NOVA-X interaction session.

    Attributes:
        mode: Current operation mode (one of :data:`MODES`).
        history: Chronological list of messages, each a dict with ``role``
            (``user`` or ``assistant``) and ``content``.
        context: Arbitrary key-value context data.
        started_at: ISO-format timestamp when the session began.
        message_count: Total number of exchanges (user + assistant pairs).
    """

    def __init__(self, mode: str = "chat") -> None:
        """Initialise a new session.

        Args:
            mode: Starting mode.  Must be a key in :data:`MODES`.
        """
        self.mode = mode if mode in MODES else "chat"
        self.history: List[Dict[str, str]] = []
        self.context: Dict[str, Any] = {}
        self.started_at: str = datetime.now().isoformat()
        self.message_count: int = 0

    # ------------------------------------------------------------------
    # Mode management
    # ------------------------------------------------------------------

    def set_mode(self, mode: str) -> bool:
        """Change the active mode.

        Args:
            mode: Desired mode key.

        Returns:
            ``True`` if the mode was valid and changed, ``False`` otherwise.
        """
        if mode in MODES:
            self.mode = mode
            return True
        return False

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the session history.

        Args:
            role: ``user`` or ``assistant``.
            content: Message text content.
        """
        self.history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        if role == "assistant":
            self.message_count += 1

    def get_history_for_ai(self, max_messages: int = 20) -> List[Dict[str, str]]:
        """Return recent history formatted for AI context.

        Args:
            max_messages: Maximum number of recent messages to include.

        Returns:
            List of dicts with ``role`` and ``content`` keys only.
        """
        recent = self.history[-max_messages:]
        return [{"role": m["role"], "content": m["content"]} for m in recent]

    def clear_history(self) -> None:
        """Erase all conversation history and reset the message counter."""
        self.history.clear()
        self.message_count = 0

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def get_mode_display_name(self) -> str:
        """Return the human-readable name of the current mode."""
        return MODE_DISPLAY_NAMES.get(self.mode, self.mode.capitalize())

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the session to a plain dictionary.

        Returns:
            Dictionary representation suitable for JSON encoding.
        """
        return {
            "mode": self.mode,
            "history": self.history,
            "context": self.context,
            "started_at": self.started_at,
            "message_count": self.message_count,
        }

"""Conversation history persistence for NOVA-X.

Manages saving and loading of chat sessions to ~/.nova_x/history/.
Each session is stored as a timestamped JSON file. The current in-memory
conversation can be flushed to disk at any time.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationHistory:
    """Persistent conversation history manager.

    Attributes:
        current_session: Messages in the active (not-yet-saved) session.
        max_history: Maximum number of messages to keep in memory.
    """

    def __init__(self, max_history: int = 500) -> None:
        """Initialise the history manager.

        Args:
            max_history: Maximum messages to retain in memory.
        """
        self._history_dir = Path.home() / ".nova_x" / "history"
        self._history_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the current in-memory session."""
        self.current_session.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.current_session) > self.max_history:
            self.current_session = self.current_session[-self.max_history:]

    def get_recent(self, n: int = 10) -> List[Dict[str, str]]:
        """Return the n most recent messages."""
        return self.current_session[-n:]

    def get_formatted_for_ai(self, n: int = 20) -> List[Dict[str, str]]:
        """Return recent messages formatted for AI context (no timestamps)."""
        return [{"role": m["role"], "content": m["content"]} for m in self.current_session[-n:]]

    def clear_current(self) -> None:
        """Clear the in-memory session."""
        self.current_session.clear()

    def save_session(self, mode: str = "chat", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Save the current session to disk. Returns the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{mode}_{timestamp}.json"
        filepath = self._history_dir / filename
        data: Dict[str, Any] = {
            "mode": mode,
            "started_at": self.current_session[0]["timestamp"] if self.current_session else datetime.now().isoformat(),
            "ended_at": datetime.now().isoformat(),
            "message_count": len(self.current_session),
            "messages": self.current_session,
        }
        if metadata:
            data["metadata"] = metadata
        try:
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"[ERROR] Failed to save session: {exc}")
        return str(filepath)

    def load_session(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a saved session from disk by filename."""
        filepath = self._history_dir / filename
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return None

    def list_sessions(self, limit: int = 20) -> List[Dict[str, str]]:
        """List saved session files ordered by recency."""
        sessions: List[Dict[str, str]] = []
        try:
            files = sorted(
                self._history_dir.glob("session_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for f in files[:limit]:
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    sessions.append({
                        "filename": f.name,
                        "mode": data.get("mode", "unknown"),
                        "date": data.get("ended_at", ""),
                        "message_count": str(data.get("message_count", 0)),
                    })
                except (json.JSONDecodeError, OSError):
                    continue
        except OSError:
            pass
        return sessions

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search session history for messages containing query."""
        results: List[Dict[str, Any]] = []
        query_lower = query.lower()
        try:
            files = sorted(
                self._history_dir.glob("session_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for f in files:
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    for msg in data.get("messages", []):
                        if query_lower in msg.get("content", "").lower():
                            results.append({**msg, "source_file": f.name})
                            if len(results) >= limit:
                                return results
                except (json.JSONDecodeError, OSError):
                    continue
        except OSError:
            pass
        return results

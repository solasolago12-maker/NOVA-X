"""Subject and assignment tracking for NOVA-X.

Manages the user's academic subjects, assignments, deadlines, and progress.
Data is stored in ~/.nova_x/subjects.json.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


COLORS = {
    "red": "#ef4444", "orange": "#f97316", "yellow": "#eab308",
    "green": "#22c55e", "blue": "#3b82f6", "purple": "#a855f7",
    "pink": "#ec4899", "cyan": "#06b6d4", "gray": "#6b7280",
}

PRIORITIES = ["low", "medium", "high", "urgent"]

STATUSES = ["pending", "in_progress", "completed", "overdue"]


class SubjectTracker:
    """Tracks subjects, assignments, deadlines, and academic progress.

    Data is automatically persisted to ~/.nova_x/subjects.json.
    """

    def __init__(self) -> None:
        """Load or create the subject tracking database."""
        self._data_dir = Path.home() / ".nova_x"
        self._data_path = self._data_dir / "subjects.json"
        self._data: Dict[str, Any] = {"subjects": {}, "assignments": {}}
        self._load()

    def _load(self) -> None:
        """Load data from disk, merging with defaults."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if self._data_path.exists():
            try:
                with open(self._data_path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                self._data = {"subjects": {}, "assignments": {}}
                self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                self._save()
        else:
            self._save()

    def _save(self) -> None:
        """Persist data to disk."""
        try:
            with open(self._data_path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"[ERROR] Failed to save subjects: {exc}")

    # -- Subject CRUD --

    def add_subject(self, name: str, color: str = "blue", description: str = "") -> None:
        """Add a new subject."""
        safe_color = color if color in COLORS else "blue"
        self._data["subjects"][name] = {
            "color": safe_color,
            "description": description,
            "added_at": datetime.now().isoformat(),
        }
        self._save()

    def remove_subject(self, name: str) -> bool:
        """Remove a subject and all associated assignments."""
        if name in self._data["subjects"]:
            del self._data["subjects"][name]
            to_remove = [
                aid for aid, a in self._data["assignments"].items()
                if a.get("subject") == name
            ]
            for aid in to_remove:
                del self._data["assignments"][aid]
            self._save()
            return True
        return False

    def get_subjects(self) -> Dict[str, Dict[str, Any]]:
        """Return all tracked subjects."""
        return dict(self._data.get("subjects", {}))

    # -- Assignment CRUD --

    def add_assignment(
        self,
        subject: str,
        title: str,
        due_date: str,
        priority: str = "medium",
        description: str = "",
    ) -> str:
        """Add a new assignment. Returns the assignment ID."""
        import uuid
        assignment_id = str(uuid.uuid4())[:8]
        safe_priority = priority if priority in PRIORITIES else "medium"
        self._data["assignments"][assignment_id] = {
            "subject": subject,
            "title": title,
            "due_date": due_date,
            "priority": safe_priority,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        self._save()
        return assignment_id

    def complete_assignment(self, assignment_id: str) -> bool:
        """Mark an assignment as completed."""
        if assignment_id in self._data["assignments"]:
            self._data["assignments"][assignment_id]["status"] = "completed"
            self._save()
            return True
        return False

    def remove_assignment(self, assignment_id: str) -> bool:
        """Delete an assignment."""
        if assignment_id in self._data["assignments"]:
            del self._data["assignments"][assignment_id]
            self._save()
            return True
        return False

    def get_assignments(self, subject: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get assignments, optionally filtered by subject and/or status."""
        assignments = self._data.get("assignments", {})
        result = {}
        for aid, a in assignments.items():
            if subject and a.get("subject") != subject:
                continue
            if status and a.get("status") != status:
                continue
            result[aid] = dict(a)
        return result

    def get_upcoming(self, days: int = 7) -> List[Dict[str, Any]]:
        """Return assignments due within the next N days."""
        now = datetime.now()
        cutoff = now + timedelta(days=days)
        upcoming: List[Dict[str, Any]] = []
        for aid, a in self._data.get("assignments", {}).items():
            if a.get("status") == "completed":
                continue
            try:
                due = datetime.fromisoformat(a["due_date"])
                if now <= due <= cutoff:
                    upcoming.append({"id": aid, **a})
            except (ValueError, KeyError):
                continue
        upcoming.sort(key=lambda x: x.get("due_date", ""))
        return upcoming

    def get_overdue(self) -> List[Dict[str, Any]]:
        """Return all overdue assignments."""
        now = datetime.now()
        overdue: List[Dict[str, Any]] = []
        for aid, a in self._data.get("assignments", {}).items():
            if a.get("status") == "completed":
                continue
            try:
                due = datetime.fromisoformat(a["due_date"])
                if due < now:
                    a_copy = dict(a)
                    a_copy["id"] = aid
                    overdue.append(a_copy)
            except (ValueError, KeyError):
                continue
        overdue.sort(key=lambda x: x.get("due_date", ""))
        return overdue

    def get_stats(self) -> Dict[str, Any]:
        """Return summary statistics."""
        assignments = self._data.get("assignments", {})
        subjects = self._data.get("subjects", {})
        total = len(assignments)
        completed = sum(1 for a in assignments.values() if a.get("status") == "completed")
        pending = sum(1 for a in assignments.values() if a.get("status") == "pending")
        overdue_list = self.get_overdue()
        return {
            "total_subjects": len(subjects),
            "total_assignments": total,
            "completed": completed,
            "pending": pending,
            "overdue": len(overdue_list),
            "completion_rate": round((completed / total) * 100, 1) if total > 0 else 0.0,
        }

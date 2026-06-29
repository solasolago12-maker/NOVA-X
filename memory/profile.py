"""User profile management for NOVA-X.

Tracks academic progress, subject proficiency, quiz performance, and
personalised recommendations.  Data is persisted to
``~/.nova_x/profile.json``.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


GRADE_LEVELS = [
    "Elementary (K-5)", "Middle School (6-8)", "High School (9-12)",
    "College / University", "Graduate", "Other",
]

SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

DEFAULT_SUBJECT = {
    "level": "Intermediate",
    "weak_areas": [],
    "strong_areas": [],
    "quizzes_taken": 0,
    "quiz_total_score": 0,
    "quiz_average": 0.0,
}


class UserProfile:
    """Persistent user profile for personalised learning assistance.

    Attributes are loaded from ``~/.nova_x/profile.json`` and provide
    methods for updating academic tracking data.
    """

    def __init__(self) -> None:
        """Load or create the user profile."""
        self._profile_dir = Path.home() / ".nova_x"
        self._profile_path = self._profile_dir / "profile.json"
        self._data: Dict[str, Any] = self._default_data()
        self._load()

    @staticmethod
    def _default_data() -> Dict[str, Any]:
        """Return the default profile structure."""
        return {
            "name": "",
            "grade_level": "",
            "subjects": {},
            "total_sessions": 0,
            "total_messages": 0,
            "quizzes_taken": 0,
            "quiz_average": 0.0,
            "weak_areas": [],
            "strong_areas": [],
        }

    def _load(self) -> None:
        """Load profile from disk, merging with defaults."""
        self._profile_dir.mkdir(parents=True, exist_ok=True)
        if self._profile_path.exists():
            try:
                with open(self._profile_path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                data = self._default_data()
                data.update(loaded)
                self._data = data
            except (json.JSONDecodeError, OSError):
                self._data = self._default_data()
                self._save()
        else:
            self._save()

    def _save(self) -> None:
        """Persist profile to disk."""
        try:
            with open(self._profile_path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            print(f"[ERROR] Failed to save profile: {exc}")

    # ------------------------------------------------------------------
    # Property accessors
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """User\'s display name."""
        return self._data.get("name", "")

    @name.setter
    def name(self, value: str) -> None:
        self._data["name"] = value
        self._save()

    @property
    def grade_level(self) -> str:
        """Current grade / education level."""
        return self._data.get("grade_level", "")

    @grade_level.setter
    def grade_level(self, value: str) -> None:
        self._data["grade_level"] = value
        self._save()

    # ------------------------------------------------------------------
    # Subject management
    # ------------------------------------------------------------------

    def add_subject(self, name: str, level: str = "Intermediate") -> None:
        """Add a subject to track.

        Args:
            name: Subject name (e.g. ``Algebra``, ``World History``).
            level: Proficiency level from :data:`SKILL_LEVELS`.
        """
        if name not in self._data["subjects"]:
            subject = dict(DEFAULT_SUBJECT)
            subject["level"] = level if level in SKILL_LEVELS else "Intermediate"
            self._data["subjects"][name] = subject
            self._save()

    def remove_subject(self, name: str) -> bool:
        """Remove a tracked subject.

        Args:
            name: Subject name to remove.

        Returns:
            ``True`` if the subject existed and was removed.
        """
        if name in self._data["subjects"]:
            del self._data["subjects"][name]
            self._save()
            return True
        return False

    def update_subject_level(self, name: str, level: str) -> bool:
        """Update a subject\'s proficiency level.

        Args:
            name: Subject name.
            level: New level from :data:`SKILL_LEVELS`.

        Returns:
            ``True`` if the subject existed and was updated.
        """
        if name in self._data["subjects"] and level in SKILL_LEVELS:
            self._data["subjects"][name]["level"] = level
            self._save()
            return True
        return False

    # ------------------------------------------------------------------
    # Strength / weakness tracking
    # ------------------------------------------------------------------

    def add_weak_area(self, area: str) -> None:
        """Record a topic the user struggles with."""
        if area not in self._data["weak_areas"]:
            self._data["weak_areas"].append(area)
            self._save()

    def add_strong_area(self, area: str) -> None:
        """Record a topic the user excels at."""
        if area not in self._data["strong_areas"]:
            self._data["strong_areas"].append(area)
            self._save()

    def get_weak_areas(self, subject: Optional[str] = None) -> List[str]:
        """Return weak areas, optionally filtered by subject.

        Args:
            subject: If given, only return weak areas for this subject.

        Returns:
            List of weak area topic strings.
        """
        if subject and subject in self._data["subjects"]:
            return list(self._data["subjects"][subject].get("weak_areas", []))
        return list(self._data.get("weak_areas", []))

    # ------------------------------------------------------------------
    # Quiz tracking
    # ------------------------------------------------------------------

    def record_quiz_result(self, subject: str, score: float, max_score: float) -> None:
        """Record a quiz result and update averages.

        Args:
            subject: Subject the quiz was for.
            score: Points earned.
            max_score: Maximum possible points.
        """
        if subject not in self._data["subjects"]:
            self.add_subject(subject)
        subj = self._data["subjects"][subject]
        subj["quizzes_taken"] = subj.get("quizzes_taken", 0) + 1
        subj["quiz_total_score"] = subj.get("quiz_total_score", 0) + score
        max_val = max_score if max_score > 0 else 1
        subj["quiz_average"] = round((subj["quiz_total_score"] / (subj["quizzes_taken"] * max_val)) * 100, 1)
        self._data["quizzes_taken"] = self._data.get("quizzes_taken", 0) + 1
        total_q = self._data["quizzes_taken"]
        total_s = sum(s.get("quiz_total_score", 0) for s in self._data["subjects"].values())
        self._data["quiz_average"] = round((total_s / (total_q * max_val)) * 100, 1) if total_q > 0 else 0.0
        self._save()

    # ------------------------------------------------------------------
    # Session tracking
    # ------------------------------------------------------------------

    def record_session(self, messages: int = 1) -> None:
        """Increment session and message counters.

        Args:
            messages: Number of new messages in the session.
        """
        self._data["total_sessions"] = self._data.get("total_sessions", 0) + 1
        self._data["total_messages"] = self._data.get("total_messages", 0) + messages
        self._save()

    # ------------------------------------------------------------------
    # Stats & recommendations
    # ------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Return a summary of user statistics.

        Returns:
            Dictionary with keys such as ``name``, ``grade_level``,
            ``total_sessions``, ``total_messages``, ``quizzes_taken``,
            ``quiz_average``, ``subjects`` (list), ``weak_areas``, and
            ``strong_areas``.
        """
        return {
            "name": self._data.get("name", ""),
            "grade_level": self._data.get("grade_level", ""),
            "total_sessions": self._data.get("total_sessions", 0),
            "total_messages": self._data.get("total_messages", 0),
            "quizzes_taken": self._data.get("quizzes_taken", 0),
            "quiz_average": self._data.get("quiz_average", 0.0),
            "subjects": list(self._data.get("subjects", {}).keys()),
            "weak_areas": list(self._data.get("weak_areas", [])),
            "strong_areas": list(self._data.get("strong_areas", [])),
        }

    def get_recommended_focus(self) -> List[str]:
        """Return a list of recommended focus areas based on weak areas and
        low-performing subjects.

        Returns:
            Ordered list of topic / subject strings to focus on.
        """
        recommendations: List[str] = []
        # Weak areas first
        recommendations.extend(self._data.get("weak_areas", []))
        # Subjects with low quiz averages
        for name, subj in self._data.get("subjects", {}).items():
            avg = subj.get("quiz_average", 100)
            if avg < 70 and name not in recommendations:
                recommendations.append(name)
        return recommendations

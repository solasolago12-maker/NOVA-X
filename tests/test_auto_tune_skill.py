import os
import sys

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from skills.auto_tune import AutoTuneSkill


def test_auto_tune_skill_explain_returns_string():
    skill = AutoTuneSkill()
    explanation = skill.explain()
    assert isinstance(explanation, str)
    assert "Auto-tune" in explanation

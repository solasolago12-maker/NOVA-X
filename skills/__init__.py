"""NOVA-X Homework Skills module.

This package contains specialized skill modules for NOVA-X, the AI homework assistant.
Each module handles a specific type of academic task:

- MathSolver: Step-by-step math problem solving with LaTeX rendering
- EssayWriter: Essay outlining, drafting, and citation management
- CodeHelper: Code writing, debugging, and optimization (20+ languages)
- ResearchAssistant: Web search and research synthesis
- QuizGenerator: Adaptive quiz generation and administration
- Explainer: Topic explanation with analogies and mind maps
"""

from .math_solver import MathSolver
from .essay_writer import EssayWriter
from .code_helper import CodeHelper
from .research import ResearchAssistant
from .quiz_generator import QuizGenerator
from .explainer import Explainer

__all__ = ["MathSolver", "EssayWriter", "CodeHelper", "ResearchAssistant", "QuizGenerator", "Explainer"]

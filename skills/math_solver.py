"""Math solver with step-by-step solutions and LaTeX rendering.

Supports algebra, calculus, geometry, statistics, trigonometry, matrices,
logarithms, and more. Uses local parsing for simple problems and AI engine
for complex ones. Formats output with LaTeX-style math for terminal display.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple


# ── LaTeX → Terminal Rendering ───────────────────────────────────────────────

# Common LaTeX symbol replacements for terminal display
_LATEX_SYMBOLS: Dict[str, str] = {
    # Greek letters
    r"\\alpha": "α",
    r"\\beta": "β",
    r"\\gamma": "γ",
    r"\\Gamma": "Γ",
    r"\\delta": "δ",
    r"\\Delta": "Δ",
    r"\\epsilon": "ε",
    r"\\zeta": "ζ",
    r"\\eta": "η",
    r"\\theta": "θ",
    r"\\Theta": "Θ",
    r"\\iota": "ι",
    r"\\kappa": "κ",
    r"\\lambda": "λ",
    r"\\Lambda": "Λ",
    r"\\mu": "μ",
    r"\\nu": "ν",
    r"\\xi": "ξ",
    r"\\Xi": "Ξ",
    r"\\pi": "π",
    r"\\Pi": "Π",
    r"\\rho": "ρ",
    r"\\sigma": "σ",
    r"\\Sigma": "Σ",
    r"\\tau": "τ",
    r"\\upsilon": "υ",
    r"\\phi": "φ",
    r"\\Phi": "Φ",
    r"\\chi": "χ",
    r"\\psi": "ψ",
    r"\\Psi": "Ψ",
    r"\\omega": "ω",
    r"\\Omega": "Ω",
    # Math symbols
    r"\\times": "×",
    r"\\div": "÷",
    r"\\pm": "±",
    r"\\cdot": "·",
    r"\\infty": "∞",
    r"\\neq": "≠",
    r"\\leq": "≤",
    r"\\geq": "≥",
    r"\\approx": "≈",
    r"\\equiv": "≡",
    r"\\rightarrow": "→",
    r"\\leftarrow": "←",
    r"\\Rightarrow": "⇒",
    r"\\Leftarrow": "⇐",
    r"\\forall": "∀",
    r"\\exists": "∃",
    r"\\in": "∈",
    r"\\notin": "∉",
    r"\\subset": "⊂",
    r"\\cup": "∪",
    r"\\cap": "∩",
    r"\\emptyset": "∅",
    r"\\nabla": "∇",
    r"\\partial": "∂",
    r"\\int": "∫",
    r"\\sum": "Σ",
    r"\\prod": "Π",
    r"\\sqrt": "√",
    r"\\frac": "/",
    r"\\degree": "°",
    r"\\angle": "∠",
    r"\\perp": "⊥",
    r"\\parallel": "‖",
    r"\\therefore": "∴",
    r"\\because": "∵",
    r"\\ldots": "…",
    r"\\cdots": "⋯",
    r"\\vdots": "⋮",
    r"\\dots": "…",
}

# Superscript and subscript digit mappings
_SUPERSCRIPT = str.maketrans("0123456789+-=()ni", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ")
_SUBSCRIPT = str.maketrans("0123456789+-=()aehklmnopstx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕₖₗₘₙₒₚₛₜₓ")


def _replace_superscripts(text: str) -> str:
    """Convert ^digits to Unicode superscripts."""
    def _replacer(match: re.Match) -> str:
        content = match.group(1)
        return content.translate(_SUPERSCRIPT)
    return re.sub(r"\^\{?([0-9+\-=.()ni]+)\}?", _replacer, text)


def _replace_subscripts(text: str) -> str:
    """Convert _digits to Unicode subscripts."""
    def _replacer(match: re.Match) -> str:
        content = match.group(1)
        return content.translate(_SUBSCRIPT)
    return re.sub(r"_\{?([0-9+a-zA-Z]+)\}?", _replacer, text)


def render_latex_terminal(latex: str) -> str:
    """Convert LaTeX math expressions to terminal-friendly Unicode.

    Handles Greek letters, math symbols, fractions, superscripts/subscripts,
    and square roots. Best-effort rendering for terminal display.

    Args:
        latex: A string containing LaTeX math (with or without $ delimiters).

    Returns:
        A Unicode string suitable for terminal display.
    """
    text = latex

    # Remove $ delimiters
    text = re.sub(r"\$(.*?)\$", r"\1", text)
    text = re.sub(r"\\\[(.*?)\\\]", r"\1", text)
    text = re.sub(r"\\\((.*?)\\\)", r"\1", text)

    # Replace \frac{a}{b} with (a)/(b)
    text = re.sub(
        r"\\frac\{([^}]+)\}\{([^}]+)\}",
        r"(\1)/(\2)",
        text,
    )

    # Replace \sqrt{x} with √x
    text = re.sub(r"\\sqrt\{([^}]+)\}", r"√(\1)", text)
    text = re.sub(r"\\sqrt\b", r"√", text)

    # Replace \int_{a}^{b} with ∫_a^b
    text = re.sub(
        r"\\int_\{([^}]+)\}\^\{([^}]+)\}",
        r"∫[\1→\2]",
        text,
    )
    text = re.sub(r"\\int\b", "∫", text)

    # Replace \sum_{n=a}^{b} with Σ_n=a^b
    text = re.sub(
        r"\\sum_\{([^}]+)\}\^\{([^}]+)\}",
        r"Σ[\1→\2]",
        text,
    )
    text = re.sub(r"\\sum\b", "Σ", text)

    # Replace symbols
    for latex_cmd, unicode_char in _LATEX_SYMBOLS.items():
        text = re.sub(latex_cmd + r"\b", unicode_char, text)

    # Handle superscripts and subscripts
    text = _replace_superscripts(text)
    text = _replace_subscripts(text)

    # Remove remaining LaTeX braces
    text = re.sub(r"\\[{}]", "", text)

    # Clean up double spaces
    text = re.sub(r" +", " ", text)

    return text.strip()


# ── MathSolution ─────────────────────────────────────────────────────────────


class MathSolution:
    """Represents a step-by-step solution to a math problem.

    Attributes:
        problem: The original problem statement.
        steps: Human-readable solution steps.
        answer: The final answer as a string.
        problem_type: Category of the problem (e.g. 'algebra_linear').
        latex_steps: Optional LaTeX-formatted versions of each step.
    """

    def __init__(
        self,
        problem: str,
        steps: List[str],
        answer: str,
        problem_type: str = "unknown",
        latex_steps: Optional[List[str]] = None,
    ) -> None:
        self.problem = problem
        self.steps = steps
        self.answer = answer
        self.problem_type = problem_type
        self.latex_steps = latex_steps or []

    def format_terminal(self) -> str:
        """Format the solution for terminal display with Rich markup.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [
            f"[bold cyan]Problem:[/] {self.problem}",
            "",
            "[bold green]Step-by-Step Solution:[/]",
        ]
        for i, step in enumerate(self.steps, 1):
            # Render any LaTeX in the step
            rendered = render_latex_terminal(step)
            lines.append(f"  [yellow]{i}.[/] {rendered}")
        lines.append("")
        rendered_answer = render_latex_terminal(self.answer)
        lines.append(f"[bold magenta]Answer: {rendered_answer}[/]")
        return "\n".join(lines)

    def format_plain(self) -> str:
        """Format the solution as plain text without Rich markup.

        Returns:
            A plain-text multi-line string.
        """
        lines = [f"Problem: {self.problem}", ""]
        lines.append("Step-by-Step Solution:")
        for i, step in enumerate(self.steps, 1):
            rendered = render_latex_terminal(step)
            lines.append(f"  {i}. {rendered}")
        lines.append("")
        lines.append(f"Answer: {render_latex_terminal(self.answer)}")
        return "\n".join(lines)


# ── MathSolver ───────────────────────────────────────────────────────────────


class MathSolver:
    """Solves math problems with step-by-step explanations.

    Automatically detects the problem type (algebra, calculus, geometry,
    statistics, etc.) and either solves it locally for simple cases or
    delegates to the AI engine for complex problems. Supports answer
    checking and practice problem generation.

    Args:
        ai_engine: An AI engine instance (e.g., core.ai_engine.AIEngine)
                   that provides a ``chat(prompt, mode=...)`` method.
    """

    PROBLEM_PATTERNS: Dict[str, str] = {
        "algebra_linear": r"(\d*)\s*\*?\s*([a-z])\s*([+\-])\s*(\d+)\s*=\s*([\d\-]+)",
        "quadratic": r"([a-z])\^2|([a-z])\s*\*\s*\2|quadratic",
        "system": r"\{.*=.*\n.*=.*\}|system|simultaneous",
        "calculus_derivative": r"derivative|differentiate|d/d|′|\\'|prime",
        "calculus_integral": r"integral|integrate|∫|antiderivative",
        "calculus_limit": r"limit|lim\s*\(",
        "geometry": r"triangle|circle|angle|area|perimeter|volume|theorem",
        "statistics": r"mean|median|mode|standard deviation|variance|probability|distribution",
        "trigonometry": r"sin\(|cos\(|tan\(|trig|cot|sec|csc",
        "matrix": r"matrix|determinant|eigenvalue|eigenvector|\[.*\].*\[.*\]",
        "logarithm": r"log\(|ln\(|logarithm|natural log",
        "exponential": r"e\^|\^\s*\(|exponential|growth|decay",
    }

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Problem Type Detection ──────────────────────────────────────────

    def detect_type(self, problem: str) -> str:
        """Detect the type of a math problem from its text.

        Scans the problem against known regex patterns for algebra,
        calculus, geometry, statistics, and other categories.

        Args:
            problem: The math problem as a string.

        Returns:
            The detected problem type key (e.g. 'algebra_linear'),
            or 'general' if no pattern matches.
        """
        problem_lower = problem.lower()
        for ptype, pattern in self.PROBLEM_PATTERNS.items():
            if re.search(pattern, problem_lower):
                return ptype
        return "general"

    # ── Main Solve Entry Point ──────────────────────────────────────────

    def solve(self, problem: str) -> MathSolution:
        """Solve a math problem step by step.

        Attempts local solving for simple linear equations and arithmetic.
        Falls back to the AI engine for complex or unrecognized problems.

        Args:
            problem: The math problem as a string.

        Returns:
            A ``MathSolution`` object containing the solution steps.
        """
        problem_type = self.detect_type(problem)

        # Try local solving for simple linear equations
        if problem_type == "algebra_linear":
            result = self._solve_linear(problem)
            if result:
                return result

        # Try local solving for simple arithmetic
        if self._is_simple_arithmetic(problem):
            result = self._solve_arithmetic(problem)
            if result:
                return result

        # Fall back to AI for complex problems
        if self.ai:
            return self._solve_with_ai(problem, problem_type)

        return MathSolution(
            problem=problem,
            steps=[
                "Could not solve locally. "
                "Please configure an AI provider for step-by-step solutions."
            ],
            answer="Unknown",
            problem_type=problem_type,
        )

    # ── Local Solvers ───────────────────────────────────────────────────

    def _solve_linear(self, problem: str) -> Optional[MathSolution]:
        """Solve linear equations of the form ax + b = c locally.

        Supports various formatting styles like ``2x + 5 = 13``,
        ``2*x + 5 = 13``, or ``-x + 3 = 7``.

        Args:
            problem: The linear equation string.

        Returns:
            A ``MathSolution`` if parsing succeeds, or ``None``.
        """
        # Remove spaces for easier parsing
        cleaned = problem.replace(" ", "")

        # Pattern: ax + b = c  (various spacing/styles)
        match = re.search(
            r"([\d\-]*)\*?\s*([a-z])\s*([+\-])\s*(\d+)\s*=\s*([\d\-]+)",
            cleaned,
        )
        if not match:
            # Try tighter pattern: 2x+5=13 or -x+3=7
            match = re.search(
                r"([\d\-]*)([a-z])([+\-])(\d+)=([\d\-]+)",
                cleaned,
            )
        if not match:
            # Try pattern with explicit multiplication: 2*x + 5 = 13
            match = re.search(
                r"([\d\-]*)\*?\s*([a-z])\s*([+\-])\s*(\d+)\s*=\s*([\d\-]+)",
                problem,
            )

        if match:
            a_str, var, op, b_str, c_str = match.groups()
            a = (
                int(a_str)
                if a_str and a_str not in ("-", "")
                else (-1 if a_str == "-" else 1)
            )
            b = int(b_str)
            c = int(c_str)
            if op == "-":
                b = -b

            # Build solution steps
            sign_b = "+" if b >= 0 else "-"
            abs_b = abs(b)

            steps = [
                f"Start with: {a}{var} {sign_b} {abs_b} = {c}",
            ]

            # Step 2: isolate the variable term
            rhs = c - b
            if b >= 0:
                steps.append(
                    f"Subtract {abs_b} from both sides: "
                    f"{a}{var} = {c} - {abs_b} = {rhs}"
                )
            else:
                steps.append(
                    f"Add {abs_b} to both sides: "
                    f"{a}{var} = {c} + {abs_b} = {rhs}"
                )

            # Step 3: solve for the variable
            if a == 1:
                steps.append(f"The variable is isolated: {var} = {rhs}")
                answer = f"{var} = {rhs}"
            elif a == -1:
                steps.append(
                    f"Multiply both sides by -1: {var} = {rhs * -1}"
                )
                answer = f"{var} = {rhs * -1}"
            else:
                result = rhs / a
                steps.append(
                    f"Divide both sides by {a}: "
                    f"{var} = {rhs} / {a} = {result}"
                )
                if rhs % a == 0:
                    answer = f"{var} = {int(result)}"
                else:
                    # Simplify fraction if possible
                    from math import gcd

                    g = gcd(abs(rhs), abs(a))
                    num = rhs // g
                    den = a // g
                    if den < 0:
                        num, den = -num, -den
                    if den == 1:
                        answer = f"{var} = {num}"
                    else:
                        answer = f"{var} = {num}/{den}  (or {result})"

            return MathSolution(
                problem=problem,
                steps=steps,
                answer=answer,
                problem_type="algebra_linear",
            )
        return None

    def _is_simple_arithmetic(self, problem: str) -> bool:
        """Check if the problem is a simple arithmetic expression.

        Returns True if the string contains only digits, operators,
        parentheses, and whitespace (no variables).
        """
        cleaned = re.sub(r"\s", "", problem)
        return bool(
            re.match(r"^[\d+\-*/().^\s]+$", cleaned)
        ) and not re.search(r"[a-zA-Z]", cleaned)

    def _solve_arithmetic(self, problem: str) -> Optional[MathSolution]:
        """Solve a simple arithmetic expression locally using eval.

        Args:
            problem: An arithmetic expression like ``2 + 3 * 4``.

        Returns:
            A ``MathSolution`` if evaluation succeeds, or ``None``.
        """
        try:
            # Replace ^ with ** for exponentiation
            cleaned = problem.replace("^", "**")
            # Security: only allow safe characters
            if not re.match(r"^[\d+\-*/().**\s]+$", cleaned):
                return None
            result = eval(cleaned, {"__builtins__": {}}, {})
            steps = [
                f"Evaluate: {problem}",
                f"Result: {result}",
            ]
            return MathSolution(
                problem=problem,
                steps=steps,
                answer=str(result),
                problem_type="arithmetic",
            )
        except Exception:
            return None

    # ── AI-Powered Solving ──────────────────────────────────────────────

    def _solve_with_ai(self, problem: str, problem_type: str) -> MathSolution:
        """Use the AI engine to solve a complex math problem.

        Sends a structured prompt to the AI and parses the response
        into individual steps and a final answer.

        Args:
            problem: The math problem text.
            problem_type: The detected problem category.

        Returns:
            A ``MathSolution`` parsed from the AI response.
        """
        prompt = (
            f"""Solve this {problem_type} math problem step by step. Show ALL work clearly.
Format each step on a new line. End with "ANSWER: [final answer]".

Problem: {problem}"""
        )

        try:
            response = self.ai.chat(prompt, mode="math")
        except Exception as e:
            return MathSolution(
                problem=problem,
                steps=[f"AI solving failed: {e}"],
                answer="Error",
                problem_type=problem_type,
            )

        # Parse steps and answer from response
        lines = [l.strip() for l in response.split("\n") if l.strip()]
        steps: List[str] = []
        answer = "See solution above"

        for line in lines:
            if line.upper().startswith("ANSWER:"):
                answer = line.split(":", 1)[1].strip()
            elif line and not line.lower().startswith("problem:"):
                steps.append(line)

        # Render LaTeX in steps
        latex_steps = [render_latex_terminal(s) for s in steps]

        return MathSolution(
            problem=problem,
            steps=steps,
            answer=answer,
            problem_type=problem_type,
            latex_steps=latex_steps,
        )

    # ── Answer Checking ─────────────────────────────────────────────────

    def check_answer(self, problem: str, user_answer: str) -> Tuple[bool, str]:
        """Check if the user's answer to a problem is correct.

        Solves the problem and compares against the user's answer using
        both string containment and numerical comparison.

        Args:
            problem: The original problem statement.
            user_answer: The user's submitted answer.

        Returns:
            A tuple of (is_correct: bool, feedback_message: str).
        """
        solution = self.solve(problem)

        # Normalize both answers
        normalized_solution = re.sub(r"\s", "", solution.answer.lower())
        normalized_user = re.sub(r"\s", "", user_answer.lower())

        # String containment check
        is_correct = (
            normalized_solution in normalized_user
            or normalized_user in normalized_solution
        )

        # Numerical comparison as fallback
        if not is_correct:
            sol_num = self._extract_number(solution.answer)
            user_num = self._extract_number(user_answer)
            if sol_num is not None and user_num is not None:
                is_correct = abs(sol_num - user_num) < 1e-9

        if is_correct:
            return True, "✓ Correct! Well done!"
        else:
            return (
                False,
                f"✗ Not quite. The correct answer is {solution.answer}. "
                "Would you like to see the steps?",
            )

    @staticmethod
    def _extract_number(text: str) -> Optional[float]:
        """Extract the first number (int or float) from a string.

        Args:
            text: A string that may contain a number.

        Returns:
            The parsed float, or ``None`` if no number is found.
        """
        match = re.search(r"-?\d+\.?\d*", text)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    # ── Practice Problem Generation ─────────────────────────────────────

    def generate_practice(self, topic: str, difficulty: str = "medium") -> str:
        """Generate a practice problem on a given topic.

        Uses the AI engine to create a new problem similar in style
        and difficulty to the requested topic.

        Args:
            topic: The math topic (e.g. 'quadratic equations').
            difficulty: One of 'easy', 'medium', or 'hard'.

        Returns:
            A problem statement string.
        """
        if self.ai:
            prompt = (
                f"Generate one {difficulty} {topic} math problem. "
                "Provide ONLY the problem statement, no solution."
            )
            try:
                return self.ai.chat(prompt, mode="math")
            except Exception as e:
                return f"Error generating practice problem: {e}"
        return "Configure an AI provider to generate practice problems."

    def explain_step(self, step_index: int, solution: MathSolution) -> str:
        """Provide a more detailed explanation for a specific solution step.

        Args:
            step_index: The 0-based index of the step to explain.
            solution: The ``MathSolution`` containing the steps.

        Returns:
            A detailed explanation of the step, or an error message.
        """
        if not (0 <= step_index < len(solution.steps)):
            return f"Invalid step index. This solution has {len(solution.steps)} steps."

        step = solution.steps[step_index]

        if self.ai:
            prompt = (
                f"Explain this math step in much more detail, "
                f"breaking it down for a student:\n\n"
                f"Problem: {solution.problem}\n"
                f"Step {step_index + 1}: {step}\n\n"
                f"Explain why this step is taken and what math rules are used."
            )
            try:
                return self.ai.chat(prompt, mode="math")
            except Exception as e:
                return f"Error explaining step: {e}"

        return f"Step {step_index + 1}: {render_latex_terminal(step)}"

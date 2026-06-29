"""Code helper for writing, debugging, explaining, and optimizing code.

Supports 20+ programming languages including Python, JavaScript, Java, C++,
C, Go, Rust, Ruby, PHP, Swift, Kotlin, TypeScript, HTML, CSS, SQL, Bash,
PowerShell, R, MATLAB, and Lua. Provides code generation, debugging,
explanation, optimization, language conversion, test case generation,
and safe Python code execution.
"""

import os
import re
import subprocess
import tempfile
import time
from typing import Dict, List, Optional, Tuple


# ── Data Classes ─────────────────────────────────────────────────────────────


class ExecutionResult:
    """Result of executing code in a subprocess.

    Attributes:
        stdout: Standard output from the program.
        stderr: Standard error from the program.
        returncode: Process exit code (0 = success).
        execution_time: Wall-clock execution time in seconds.
        success: Convenience property, True if returncode == 0.
    """

    def __init__(
        self,
        stdout: str,
        stderr: str,
        returncode: int,
        execution_time: float = 0.0,
    ) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.execution_time = execution_time
        self.success = returncode == 0

    def format_terminal(self) -> str:
        """Format the execution result for terminal display with Rich markup.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = []
        if self.stdout:
            lines.append(f"[bold green]Output:[/]\n{self.stdout}")
        if self.stderr:
            lines.append(f"[bold red]Errors:[/]\n{self.stderr}")
        lines.append(
            f"[dim]Exit code: {self.returncode} | "
            f"Time: {self.execution_time:.2f}s[/]"
        )
        return "\n".join(lines)

    def format_plain(self) -> str:
        """Format the execution result as plain text.

        Returns:
            A plain-text multi-line string.
        """
        lines = []
        if self.stdout:
            lines.append(f"Output:\n{self.stdout}")
        if self.stderr:
            lines.append(f"Errors:\n{self.stderr}")
        lines.append(f"Exit code: {self.returncode} | Time: {self.execution_time:.2f}s")
        return "\n".join(lines)


# ── CodeHelper ───────────────────────────────────────────────────────────────


class CodeHelper:
    """Helps with code across 20+ programming languages.

    Provides AI-powered code generation, debugging, explanation,
    optimization, language conversion, and test case generation.
    Can execute Python code safely in a subprocess.

    Args:
        ai_engine: An AI engine instance that provides ``chat()``.
    """

    LANGUAGES: Dict[str, Dict[str, str]] = {
        "python": {"ext": ".py", "cmd": "python", "comment": "#"},
        "javascript": {"ext": ".js", "cmd": "node", "comment": "//"},
        "java": {"ext": ".java", "cmd": "javac && java", "comment": "//"},
        "cpp": {"ext": ".cpp", "cmd": "g++ -o out && ./out", "comment": "//"},
        "c": {"ext": ".c", "cmd": "gcc -o out && ./out", "comment": "//"},
        "go": {"ext": ".go", "cmd": "go run", "comment": "//"},
        "rust": {"ext": ".rs", "cmd": "rustc && ./out", "comment": "//"},
        "ruby": {"ext": ".rb", "cmd": "ruby", "comment": "#"},
        "php": {"ext": ".php", "cmd": "php", "comment": "//"},
        "swift": {"ext": ".swift", "cmd": "swift", "comment": "//"},
        "kotlin": {"ext": ".kt", "cmd": "kotlinc && kotlin", "comment": "//"},
        "typescript": {"ext": ".ts", "cmd": "ts-node", "comment": "//"},
        "html": {"ext": ".html", "cmd": "browser", "comment": "<!--"},
        "css": {"ext": ".css", "cmd": "browser", "comment": "/*"},
        "sql": {"ext": ".sql", "cmd": "sql", "comment": "--"},
        "bash": {"ext": ".sh", "cmd": "bash", "comment": "#"},
        "powershell": {"ext": ".ps1", "cmd": "powershell", "comment": "#"},
        "r": {"ext": ".r", "cmd": "Rscript", "comment": "#"},
        "matlab": {"ext": ".m", "cmd": "matlab", "comment": "%"},
        "lua": {"ext": ".lua", "cmd": "lua", "comment": "--"},
        "perl": {"ext": ".pl", "cmd": "perl", "comment": "#"},
        "scala": {"ext": ".scala", "cmd": "scala", "comment": "//"},
        "dart": {"ext": ".dart", "cmd": "dart", "comment": "//"},
        "elixir": {"ext": ".ex", "cmd": "elixir", "comment": "#"},
    }

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Code Generation ─────────────────────────────────────────────────

    def write_code(self, description: str, language: str = "python") -> str:
        """Generate code from a natural language description.

        Args:
            description: What the code should do.
            language: Target programming language.

        Returns:
            The generated code as a string.
        """
        if not self.ai:
            return "Configure AI to generate code."

        lang_info = self.LANGUAGES.get(
            language.lower(), self.LANGUAGES["python"]
        )
        prompt = f"""Write clean, well-commented {language} code for: {description}
Include comments explaining the logic. Use best practices and proper error handling.
Provide ONLY the code, no extra explanations outside the code comments."""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error generating code: {e}"

    def write_function(
        self,
        description: str,
        inputs: List[str],
        outputs: List[str],
        language: str = "python",
    ) -> str:
        """Generate a specific function with defined inputs/outputs.

        Args:
            description: What the function should do.
            inputs: List of input parameter descriptions.
            outputs: List of return value descriptions.
            language: Target programming language.

        Returns:
            The generated function code.
        """
        if not self.ai:
            return "Configure AI to generate code."

        inputs_str = "\n".join(f"  - {inp}" for inp in inputs)
        outputs_str = "\n".join(f"  - {out}" for out in outputs)

        prompt = f"""Write a {language} function with these specifications:

Description: {description}

Inputs:
{inputs_str}

Returns:
{outputs_str}

Include:
- Docstring/comments explaining the function
- Input validation
- Error handling
- Example usage in comments"""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error generating function: {e}"

    # ── Debugging ───────────────────────────────────────────────────────

    def debug(self, code: str, error: str = "", language: str = "python") -> str:
        """Debug code with an optional error message.

        Args:
            code: The buggy code.
            error: The error message (optional).
            language: Programming language.

        Returns:
            Debugging analysis and fixed code.
        """
        if not self.ai:
            return "Configure AI for debugging help."

        error_text = f"\nError message: {error}" if error else "\nIt has a bug. Find and fix it."

        prompt = f"""Debug this {language} code.{error_text}

Code:
```{language}
{code}
```

Provide:
1. What the bug is (brief explanation)
2. The fixed code in a code block
3. Explanation of the fix"""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error debugging code: {e}"

    # ── Code Explanation ────────────────────────────────────────────────

    def explain(self, code: str, language: str = "python") -> str:
        """Explain what code does line by line.

        Args:
            code: The code to explain.
            language: Programming language.

        Returns:
            A detailed explanation of the code.
        """
        if not self.ai:
            return "Configure AI for code explanation."

        prompt = f"""Explain this {language} code line by line:

```{language}
{code}
```

Explain what each part does and the overall purpose. Be educational and clear."""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error explaining code: {e}"

    def explain_algorithm(self, algorithm_name: str, language: str = "python") -> str:
        """Explain a named algorithm and provide an implementation.

        Args:
            algorithm_name: Name of the algorithm (e.g. 'quicksort').
            language: Target language for the implementation.

        Returns:
            Explanation and code implementation.
        """
        if not self.ai:
            return "Configure AI for algorithm explanation."

        prompt = f"""Explain the {algorithm_name} algorithm in simple terms.
Then provide a clean {language} implementation with comments.

Structure:
1. Overview - what it does
2. How it works - step by step
3. Time and space complexity
4. Implementation in {language}
5. Example usage"""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error explaining algorithm: {e}"

    # ── Optimization ────────────────────────────────────────────────────

    def optimize(self, code: str, language: str = "python") -> str:
        """Optimize code for performance and readability.

        Args:
            code: The code to optimize.
            language: Programming language.

        Returns:
            The optimized version with improvement notes.
        """
        if not self.ai:
            return "Configure AI for code optimization."

        prompt = f"""Optimize this {language} code for better performance and readability:

```{language}
{code}
```

Provide the optimized version with comments explaining the improvements.
Focus on:
- Algorithm efficiency (time/space complexity)
- Pythonic idioms (if Python) or language best practices
- Readability and maintainability
- Edge case handling"""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error optimizing code: {e}"

    # ── Language Conversion ─────────────────────────────────────────────

    def convert(self, code: str, from_lang: str, to_lang: str) -> str:
        """Convert code from one programming language to another.

        Args:
            code: The source code.
            from_lang: Source programming language.
            to_lang: Target programming language.

        Returns:
            The converted code.
        """
        if not self.ai:
            return "Configure AI for code conversion."

        prompt = f"""Convert this {from_lang} code to {to_lang}:

```{from_lang}
{code}
```

Maintain the exact same functionality. Add comments in the {to_lang} version explaining key differences. Use idiomatic {to_lang} patterns."""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error converting code: {e}"

    # ── Test Case Generation ────────────────────────────────────────────

    def test_cases(self, code: str, language: str = "python") -> List[str]:
        """Generate test cases for code.

        Args:
            code: The code to generate tests for.
            language: Programming language.

        Returns:
            A list of test case strings.
        """
        if not self.ai:
            return ["Configure AI to generate test cases."]

        prompt = f"""Generate test cases (unit tests) for this {language} code:

```{language}
{code}
```

Provide test cases covering:
- Normal/expected cases
- Edge cases (empty input, single element, etc.)
- Error cases (invalid input, exceptions)

Format each test case as: "Test: [name] - Input: [input] - Expected: [output]"
"""

        try:
            response = self.ai.chat(prompt, mode="code")
        except Exception as e:
            return [f"Error generating test cases: {e}"]

        # Parse test cases from response
        tests = []
        for line in response.split("\n"):
            line = line.strip()
            if line and (
                line.lower().startswith("test:")
                or line.lower().startswith("- test")
                or line.lower().startswith(">>>")
                or "input:" in line.lower()
            ):
                tests.append(line)

        return tests if tests else [t.strip() for t in response.split("\n") if t.strip()]

    def generate_unit_tests(self, code: str, language: str = "python") -> str:
        """Generate runnable unit test code.

        Args:
            code: The code to generate unit tests for.
            language: Programming language.

        Returns:
            A string containing runnable unit test code.
        """
        if not self.ai:
            return "Configure AI to generate unit tests."

        prompt = f"""Generate complete, runnable unit tests for this {language} code.
Use the standard testing framework for {language} (e.g., unittest for Python, Jest for JavaScript).

Code to test:
```{language}
{code}
```

Provide ONLY the test code, ready to run."""

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error generating unit tests: {e}"

    # ── Code Execution ──────────────────────────────────────────────────

    def run_code(self, code: str, language: str = "python") -> ExecutionResult:
        """Execute Python code safely in a subprocess.

        Runs the code in a temporary file with a timeout. Only Python
        is supported for direct execution; other languages require
        their own compilers/interpreters.

        Args:
            code: The Python code to run.
            language: Programming language (only 'python' supported).

        Returns:
            An ``ExecutionResult`` with stdout, stderr, and timing.
        """
        if language.lower() != "python":
            return ExecutionResult(
                "",
                f"Direct execution only supported for Python. "
                f"Use a {language} compiler/interpreter for {language} code.",
                1,
            )

        start = time.time()

        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python", temp_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = time.time() - start
            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                execution_time=elapsed,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                "",
                "Execution timed out (30s limit)",
                -1,
                time.time() - start,
            )
        except FileNotFoundError:
            return ExecutionResult(
                "",
                "Python interpreter not found. Make sure Python is installed.",
                -1,
                time.time() - start,
            )
        except Exception as e:
            return ExecutionResult(
                "",
                str(e),
                -1,
                time.time() - start,
            )
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def check_syntax(self, code: str, language: str = "python") -> Tuple[bool, str]:
        """Check if Python code has valid syntax without executing it.

        Args:
            code: The Python code to check.
            language: Programming language (only 'python' supported).

        Returns:
            A tuple of (is_valid: bool, message: str).
        """
        if language.lower() != "python":
            return (
                False,
                f"Syntax checking only supported for Python, not {language}.",
            )

        import py_compile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            py_compile.compile(temp_path, doraise=True)
            return True, "Syntax is valid."
        except py_compile.PyCompileError as e:
            return False, f"Syntax error: {e}"
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    # ── Utility ─────────────────────────────────────────────────────────

    def get_language_info(self, language: str) -> Dict[str, str]:
        """Get information about a supported language.

        Args:
            language: The language name.

        Returns:
            A dict with 'ext', 'cmd', and 'comment' keys, or empty dict.
        """
        return self.LANGUAGES.get(language.lower(), {})

    def list_languages(self) -> List[str]:
        """Get a list of all supported programming languages.

        Returns:
            A sorted list of language names.
        """
        return sorted(self.LANGUAGES.keys())

    def add_comments(self, code: str, language: str = "python") -> str:
        """Add explanatory comments to existing code.

        Args:
            code: The code to add comments to.
            language: Programming language.

        Returns:
            The code with added comments.
        """
        if not self.ai:
            return "Configure AI to add comments."

        prompt = (
            f"Add helpful comments to this {language} code. "
            "Do not change the logic, just add comments explaining "
            "what each section does:\n\n"
            f"```{language}\n"
            f"{code}\n"
            f"```\n\n"
            "Return the fully commented code."
        )

        try:
            return self.ai.chat(prompt, mode="code")
        except Exception as e:
            return f"Error adding comments: {e}"

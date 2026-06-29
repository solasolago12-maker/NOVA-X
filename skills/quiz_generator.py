"""Quiz generator for practice questions and adaptive learning.

Generates quizzes with multiple question types (multiple choice, true/false,
short answer, fill-in-the-blank), administers them interactively, reviews
mistakes, and creates adaptive quizzes targeting weak areas.
"""

import random
import re
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class Question:
    """A single quiz question.

    Attributes:
        question: The question text.
        question_type: One of 'multiple_choice', 'true_false',
                       'short_answer', 'fill_blank'.
        options: List of answer options (for multiple choice).
        correct_answer: The correct answer string.
        explanation: Explanation of the correct answer.
        difficulty: One of 'easy', 'medium', 'hard'.
    """

    question: str
    question_type: str  # multiple_choice, true_false, short_answer, fill_blank
    options: List[str] = field(default_factory=list)
    correct_answer: str = ""
    explanation: str = ""
    difficulty: str = "medium"

    def format_terminal(self) -> str:
        """Format the question for terminal display.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [f"[bold yellow]{self.question}[/]"]

        if self.question_type == "multiple_choice" and self.options:
            for j, opt in enumerate(self.options):
                lines.append(f"  {chr(65 + j)}. {opt}")
        elif self.question_type == "true_false":
            lines.append("  [True / False]")
        elif self.question_type == "fill_blank":
            lines.append("  [Fill in the blank]")

        return "\n".join(lines)


@dataclass
class Quiz:
    """A quiz containing multiple questions.

    Attributes:
        topic: The quiz topic.
        questions: List of ``Question`` objects.
        difficulty: Overall difficulty level.
    """

    topic: str
    questions: List[Question] = field(default_factory=list)
    difficulty: str = "medium"

    @property
    def total_points(self) -> int:
        """Return the total number of questions."""
        return len(self.questions)

    def format_terminal(self) -> str:
        """Format the full quiz for terminal display.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [
            f"[bold cyan]{'=' * 50}[/]",
            f"[bold white]Quiz: {self.topic}[/] "
            f"[dim]({self.difficulty})[/]",
            f"[bold cyan]{'=' * 50}[/]",
            f"[dim]{self.total_points} questions[/]\n",
        ]

        for i, q in enumerate(self.questions, 1):
            lines.append(f"[bold]Question {i}:[/]")
            lines.append(q.format_terminal())
            lines.append("")

        return "\n".join(lines)


@dataclass
class QuizResult:
    """Result of taking a quiz.

    Attributes:
        quiz: The ``Quiz`` that was taken.
        answers: Dict mapping question index to user's answer.
        score: Number of correct answers.
        time_taken: Time taken in seconds.
    """

    quiz: Quiz
    answers: Dict[int, str] = field(default_factory=dict)
    score: int = 0
    time_taken: int = 0

    @property
    def percentage(self) -> float:
        """Return the score as a percentage."""
        return (
            (self.score / self.quiz.total_points * 100)
            if self.quiz.total_points > 0
            else 0.0
        )

    @property
    def grade(self) -> str:
        """Return a letter grade based on the percentage."""
        pct = self.percentage
        if pct >= 90:
            return "A"
        elif pct >= 80:
            return "B"
        elif pct >= 70:
            return "C"
        elif pct >= 60:
            return "D"
        else:
            return "F"

    @property
    def wrong_questions(self) -> List[int]:
        """Return indices of questions answered incorrectly."""
        wrong = []
        for i, q in enumerate(self.quiz.questions):
            user_ans = self.answers.get(i, "").lower().strip()
            correct = q.correct_answer.lower().strip()

            # Flexible comparison for multiple choice
            if q.question_type == "multiple_choice" and q.options:
                # Accept either letter or full text
                if user_ans in ("a", "b", "c", "d"):
                    idx = ord(user_ans) - ord("a")
                    if 0 <= idx < len(q.options):
                        user_ans = q.options[idx].lower().strip()

            if user_ans != correct:
                wrong.append(i)
        return wrong

    def format_terminal(self) -> str:
        """Format the quiz result for terminal display.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        pct = self.percentage
        grade_color = {
            "A": "bold green",
            "B": "green",
            "C": "yellow",
            "D": "orange3",
            "F": "bold red",
        }.get(self.grade, "white")

        lines = [
            f"[bold cyan]{'=' * 50}[/]",
            f"[bold white]Quiz Results: {self.quiz.topic}[/]",
            f"[bold cyan]{'=' * 50}[/]",
            "",
            f"Score: [bold]{self.score}/{self.quiz.total_points}[/] "
            f"({pct:.1f}%)",
            f"Grade: [{grade_color}]{self.grade}[/{grade_color}]",
            f"Time: {self.time_taken}s",
            "",
        ]

        # Per-question breakdown
        for i, q in enumerate(self.quiz.questions):
            user_ans = self.answers.get(i, "No answer")
            is_correct = i not in self.wrong_questions
            icon = "[green]✓[/]" if is_correct else "[red]✗[/]"
            lines.append(
                f"{icon} Q{i + 1}: Your answer: {user_ans} | "
                f"Correct: {q.correct_answer}"
            )

        return "\n".join(lines)


# ── QuizGenerator ────────────────────────────────────────────────────────────


class QuizGenerator:
    """Generates practice quizzes on any topic.

    Creates quizzes with various question types, administers them
    interactively, and generates adaptive quizzes targeting weak areas.

    Args:
        ai_engine: An AI engine instance that provides ``chat()``.
    """

    QUESTION_TYPES = [
        "multiple_choice",
        "true_false",
        "short_answer",
        "fill_blank",
    ]

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Quiz Generation ─────────────────────────────────────────────────

    def generate(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_types: Optional[List[str]] = None,
    ) -> Quiz:
        """Generate a quiz on a topic.

        Args:
            topic: The quiz topic or subject.
            num_questions: Number of questions to generate.
            difficulty: One of 'easy', 'medium', 'hard'.
            question_types: List of question type strings, or None for all.

        Returns:
            A ``Quiz`` object with generated questions.
        """
        if not self.ai:
            return Quiz(
                topic=topic,
                questions=[
                    Question(
                        question="Configure AI to generate quizzes",
                        question_type="short_answer",
                        correct_answer="ok",
                    )
                ],
            )

        types_str = (
            ", ".join(question_types)
            if question_types
            else "multiple_choice, true_false, short_answer"
        )

        prompt = f"""Create a {difficulty} quiz about: {topic}
Number of questions: {num_questions}
Question types: {types_str}

Format EACH question EXACTLY as:
Q: [question text]
TYPE: [multiple_choice / true_false / short_answer / fill_blank]
OPTIONS: [for MC: A) option1 B) option2 C) option3 D) option4]
ANSWER: [correct answer]
EXPLANATION: [why this is correct]
---"""

        try:
            response = self.ai.chat(prompt, mode="quiz")
        except Exception as e:
            return Quiz(
                topic=topic,
                questions=[
                    Question(
                        question=f"Error generating quiz: {e}",
                        question_type="short_answer",
                        correct_answer="error",
                    )
                ],
            )

        return self._parse_quiz(topic, response, difficulty)

    def _parse_quiz(self, topic: str, text: str, difficulty: str) -> Quiz:
        """Parse a quiz from AI response text.

        Args:
            topic: The quiz topic.
            text: The AI-generated quiz text.
            difficulty: The difficulty level.

        Returns:
            A ``Quiz`` object with parsed questions.
        """
        quiz = Quiz(topic=topic, difficulty=difficulty)
        questions_raw = text.split("---")

        for q_text in questions_raw:
            q_text = q_text.strip()
            if not q_text or "Q:" not in q_text:
                continue

            question = ""
            q_type = "short_answer"
            options: List[str] = []
            answer = ""
            explanation = ""

            for line in q_text.split("\n"):
                line = line.strip()
                if line.startswith("Q:"):
                    question = line[2:].strip()
                elif line.startswith("TYPE:"):
                    q_type = line[5:].strip().lower()
                elif line.startswith("OPTIONS:"):
                    opts_text = line[8:].strip()
                    # Parse A) option B) option format
                    options = [
                        o.strip()
                        for o in re.split(r"[A-D]\)", opts_text)
                        if o.strip()
                    ]
                elif line.startswith("ANSWER:"):
                    answer = line[7:].strip()
                elif line.startswith("EXPLANATION:"):
                    explanation = line[12:].strip()

            if question:
                quiz.questions.append(
                    Question(
                        question=question,
                        question_type=q_type,
                        options=options,
                        correct_answer=answer,
                        explanation=explanation,
                        difficulty=difficulty,
                    )
                )

        return quiz

    # ── Notes-Based Generation ──────────────────────────────────────────

    def generate_from_notes(
        self, notes: str, num_questions: int = 5
    ) -> Quiz:
        """Generate a quiz from student's study notes.

        Args:
            notes: The study notes text.
            num_questions: Number of questions to generate.

        Returns:
            A ``Quiz`` based on the notes.
        """
        if not self.ai:
            return Quiz(
                topic="From Notes",
                questions=[],
            )

        # Truncate notes if too long
        notes_truncated = notes[:3000]

        prompt = f"""Create a quiz based on these study notes:

{notes_truncated}

Generate {num_questions} questions testing understanding of these notes.
Include a mix of multiple choice and short answer questions.

Format EACH question EXACTLY as:
Q: [question text]
TYPE: [multiple_choice / short_answer]
OPTIONS: [for MC: A) option1 B) option2 C) option3 D) option4]
ANSWER: [correct answer]
EXPLANATION: [why this is correct]
---"""

        try:
            response = self.ai.chat(prompt, mode="quiz")
        except Exception as e:
            return Quiz(
                topic="From Notes",
                questions=[
                    Question(
                        question=f"Error: {e}",
                        question_type="short_answer",
                        correct_answer="error",
                    )
                ],
            )

        return self._parse_quiz("From Notes", response, "medium")

    # ── Quiz Administration ─────────────────────────────────────────────

    def administer(self, quiz: Quiz) -> QuizResult:
        """Administer a quiz interactively in the terminal.

        Asks each question and collects user answers, tracking score
        and time taken.

        Args:
            quiz: The ``Quiz`` to administer.

        Returns:
            A ``QuizResult`` with answers and score.
        """
        result = QuizResult(quiz=quiz)

        print(f"\n[bold cyan]Quiz: {quiz.topic}[/] ({quiz.difficulty})")
        print(f"[dim]{quiz.total_points} questions[/]\n")

        start_time = time.time()

        for i, q in enumerate(quiz.questions):
            print(f"[bold yellow]Q{i + 1}.[/] {q.question}")

            if q.question_type == "multiple_choice" and q.options:
                for j, opt in enumerate(q.options):
                    print(f"  {chr(65 + j)}. {opt}")
            elif q.question_type == "true_false":
                print("  True / False")
            elif q.question_type == "fill_blank":
                print("  [Fill in the blank]")

            try:
                answer = input("\nYour answer: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[dim]Quiz interrupted.[/]")
                break

            result.answers[i] = answer

            # Check answer
            is_correct = self._check_answer(q, answer)

            if is_correct:
                print("[bold green]✓ Correct![/]\n")
                result.score += 1
            else:
                print(
                    f"[bold red]✗ The correct answer is: "
                    f"{q.correct_answer}[/]"
                )
                if q.explanation:
                    print(f"[dim]{q.explanation}[/]")
                print()

        result.time_taken = int(time.time() - start_time)

        print(
            f"[bold magenta]Score: {result.score}/{quiz.total_points} "
            f"({result.percentage:.0f}%)[/]\n"
        )

        return result

    @staticmethod
    def _check_answer(question: Question, user_answer: str) -> bool:
        """Check if a user's answer matches the correct answer.

        Handles flexible matching for multiple choice (accepts letter
        or full text) and case-insensitive comparison.

        Args:
            question: The ``Question`` being checked.
            user_answer: The user's answer string.

        Returns:
            True if the answer is correct.
        """
        user_ans = user_answer.lower().strip()
        correct = question.correct_answer.lower().strip()

        if not user_ans:
            return False

        # Direct match
        if user_ans == correct:
            return True

        # Multiple choice letter answer
        if (
            question.question_type == "multiple_choice"
            and question.options
        ):
            if user_ans in ("a", "b", "c", "d"):
                idx = ord(user_ans) - ord("a")
                if 0 <= idx < len(question.options):
                    return question.options[idx].lower().strip() == correct

        # Containment check
        if user_ans in correct or correct in user_ans:
            return True

        # True/False flexible matching
        if question.question_type == "true_false":
            user_bool = user_ans in ("true", "t", "yes", "y", "1")
            correct_bool = correct in ("true", "t", "yes", "y", "1")
            return user_bool == correct_bool

        return False

    # ── Mistake Review ──────────────────────────────────────────────────

    def review_mistakes(self, result: QuizResult) -> str:
        """Review wrong answers with explanations.

        Args:
            result: The ``QuizResult`` to review.

        Returns:
            A formatted review string.
        """
        if not result.wrong_questions:
            return "[bold green]Perfect score! No mistakes to review.[/]"

        lines = ["[bold cyan]Review of Mistakes:[/]\n"]

        for idx in result.wrong_questions:
            q = result.quiz.questions[idx]
            lines.append(f"[yellow]Q{idx + 1}:[/] {q.question}")
            lines.append(
                f"  Your answer: {result.answers.get(idx, 'No answer')}"
            )
            lines.append(f"  Correct: [green]{q.correct_answer}[/]")
            if q.explanation:
                lines.append(f"  [dim]{q.explanation}[/]")
            lines.append("")

        # Add study tip
        lines.append(
            "[bold yellow]Tip:[/] Focus on these topics for your next quiz!"
        )

        return "\n".join(lines)

    # ── Adaptive Quizzes ────────────────────────────────────────────────

    def adaptive_quiz(
        self, subject: str, weak_areas: List[str]
    ) -> Quiz:
        """Generate a quiz targeting weak areas.

        Creates challenging questions specifically about the topics
        the student needs to improve on.

        Args:
            subject: The overall subject name.
            weak_areas: List of specific weak topic areas.

        Returns:
            An adaptive ``Quiz`` targeting weak areas.
        """
        if not self.ai or not weak_areas:
            return self.generate(subject, difficulty="hard")

        areas_text = ", ".join(weak_areas)

        prompt = f"""Create a focused quiz about {subject} targeting these weak areas: {areas_text}

Generate challenging questions specifically about: {areas_text}
Include detailed explanations for learning.

Format EACH question EXACTLY as:
Q: [question text]
TYPE: [multiple_choice / true_false / short_answer]
OPTIONS: [for MC: A) option1 B) option2 C) option3 D) option4]
ANSWER: [correct answer]
EXPLANATION: [detailed explanation to help the student learn]
---"""

        try:
            response = self.ai.chat(prompt, mode="quiz")
        except Exception as e:
            return Quiz(
                topic=f"{subject} - Adaptive",
                questions=[
                    Question(
                        question=f"Error: {e}",
                        question_type="short_answer",
                        correct_answer="error",
                    )
                ],
            )

        return self._parse_quiz(f"{subject} - Adaptive", response, "hard")

    # ── Flashcard Generation ────────────────────────────────────────────

    def generate_flashcards(
        self, topic: str, num_cards: int = 10
    ) -> List[Dict[str, str]]:
        """Generate flashcards for a topic.

        Args:
            topic: The topic to create flashcards for.
            num_cards: Number of flashcards to generate.

        Returns:
            A list of dicts with 'front' and 'back' keys.
        """
        if not self.ai:
            return [{"front": "Configure AI", "back": "to generate flashcards"}]

        prompt = f"""Create {num_cards} flashcards about: {topic}

Format each flashcard as:
FRONT: [question or term]
BACK: [answer or definition]
---"""

        try:
            response = self.ai.chat(prompt, mode="quiz")
        except Exception as e:
            return [{"front": "Error", "back": str(e)}]

        # Parse flashcards
        cards: List[Dict[str, str]] = []
        raw_cards = response.split("---")

        for card_text in raw_cards:
            card_text = card_text.strip()
            if not card_text:
                continue

            front = ""
            back = ""

            for line in card_text.split("\n"):
                line = line.strip()
                if line.startswith("FRONT:"):
                    front = line[6:].strip()
                elif line.startswith("BACK:"):
                    back = line[5:].strip()

            if front and back:
                cards.append({"front": front, "back": back})

        return cards

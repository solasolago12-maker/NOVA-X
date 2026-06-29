"""Topic explainer with analogies, summaries, and mind maps.

Provides educational explanations at different difficulty levels,
creates relatable analogies for complex concepts, summarizes long
texts, extracts and defines key terms, and generates text-based
mind maps for visual learning.
"""

from typing import Dict, List, Optional


# ── Explainer ────────────────────────────────────────────────────────────────


class Explainer:
    """Explains complex topics in simple, understandable terms.

    Supports multiple explanation levels (simple/medium/detailed),
creates everyday analogies, summarizes texts, defines key terms,
    and generates ASCII mind maps.

    Args:
        ai_engine: An AI engine instance that provides ``chat()``.
    """

    LEVELS: Dict[str, str] = {
        "simple": (
            "Explain like I'm 10 years old (ELI5). Use simple words, "
            "fun examples, and avoid jargon."
        ),
        "medium": (
            "Explain at a high school level. Use some technical terms "
            "but define them clearly."
        ),
        "detailed": (
            "Explain at a college/university level with technical depth. "
            "Include formal definitions, theories, and references."
        ),
        "expert": (
            "Explain at a graduate/research level with maximum technical "
            "depth, citing theories, equations, and current research."
        ),
    }

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Topic Explanation ───────────────────────────────────────────────

    def explain(
        self,
        topic: str,
        level: str = "medium",
        context: str = "",
    ) -> str:
        """Explain a topic at the specified level.

        Args:
            topic: The topic to explain.
            level: One of 'simple', 'medium', 'detailed', 'expert'.
            context: Optional context about why the user wants to learn this.

        Returns:
            A detailed explanation string.
        """
        if not self.ai:
            return (
                f"Configure AI to explain topics. "
                f"Requested: {topic} at {level} level."
            )

        level_desc = self.LEVELS.get(level, self.LEVELS["medium"])
        context_text = f"\nContext: {context}" if context else ""

        prompt = f"""{level_desc}

Topic: {topic}{context_text}

Provide:
1. A clear, engaging explanation
2. Key concepts with definitions
3. Real-world examples or applications
4. A simple analogy if helpful
5. Common misconceptions (if any)

Make it educational and easy to understand."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error explaining topic: {e}"

    # ── Analogies ───────────────────────────────────────────────────────

    def analogize(self, concept: str) -> str:
        """Create a relatable everyday analogy for a concept.

        Args:
            concept: The concept to create an analogy for.

        Returns:
            An analogy explanation string.
        """
        if not self.ai:
            return "Configure AI to create analogies."

        prompt = f"""Create a relatable, everyday analogy for this concept:
{concept}

The analogy should:
- Use something familiar from daily life
- Map the key elements accurately
- Help someone understand the concept intuitively

Format your response as:
"[Concept] is like [analogy] because..."

Then explain the mapping between the analogy and the concept in detail."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error creating analogy: {e}"

    def compare_concepts(
        self, concept_a: str, concept_b: str
    ) -> str:
        """Compare and contrast two related concepts.

        Args:
            concept_a: First concept.
            concept_b: Second concept.

        Returns:
            A comparison explanation.
        """
        if not self.ai:
            return "Configure AI to compare concepts."

        prompt = f"""Compare and contrast these two concepts:

Concept A: {concept_a}
Concept B: {concept_b}

Provide:
1. How they are similar
2. How they are different
3. When to use each
4. A simple analogy for each

Format as a clear, educational comparison."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error comparing concepts: {e}"

    # ── Text Summarization ──────────────────────────────────────────────

    def summarize_text(
        self, text: str, max_words: int = 100
    ) -> str:
        """Summarize a long text to a target word count.

        Args:
            text: The text to summarize.
            max_words: Maximum number of words in the summary.

        Returns:
            A concise summary.
        """
        if not self.ai:
            return "Configure AI for text summarization."

        # Truncate if too long
        text_input = text[:4000] if len(text) > 4000 else text

        prompt = f"""Summarize the following text in about {max_words} words:

{text_input}

Provide a concise summary capturing the main points."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error summarizing: {e}"

    def summarize_bullet_points(
        self, text: str, num_points: int = 5
    ) -> List[str]:
        """Summarize a text as a list of bullet points.

        Args:
            text: The text to summarize.
            num_points: Number of bullet points to generate.

        Returns:
            A list of summary bullet point strings.
        """
        if not self.ai:
            return ["Configure AI for summarization."]

        text_input = text[:4000] if len(text) > 4000 else text

        prompt = f"""Summarize the following text as {num_points} bullet points:

{text_input}

Format as:
• [point 1]
• [point 2]
• [point 3]
etc."""

        try:
            response = self.ai.chat(prompt, mode="explain")
            return [
                line.strip().lstrip("•- ")
                for line in response.split("\n")
                if line.strip() and line.strip()[0] in "•-"
            ]
        except Exception as e:
            return [f"Error: {e}"]

    # ── Term Definitions ────────────────────────────────────────────────

    def define_terms(self, text: str) -> Dict[str, str]:
        """Extract and define key technical terms from text.

        Args:
            text: The text to extract terms from.

        Returns:
            A dict mapping terms to their definitions.
        """
        if not self.ai:
            return {"Error": "Configure AI for term extraction."}

        text_input = text[:3000] if len(text) > 3000 else text

        prompt = f"""Extract and define the key technical terms from this text:

{text_input}

Format as:
TERM: definition
TERM: definition

Only include important technical/academic terms. Keep definitions clear and concise."""

        try:
            response = self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return {"Error": str(e)}

        terms: Dict[str, str] = {}
        for line in response.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                parts = line.split(":", 1)
                term = parts[0].strip().replace("TERM", "").strip()
                definition = parts[1].strip()
                if term and definition:
                    terms[term] = definition

        return terms

    def define_single_term(self, term: str) -> str:
        """Define a single technical or academic term.

        Args:
            term: The term to define.

        Returns:
            A clear definition string.
        """
        if not self.ai:
            return "Configure AI for term definition."

        prompt = f"""Define this term clearly and concisely:

Term: {term}

Provide:
1. A clear definition
2. A simple example
3. Related terms (if any)"""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error defining term: {e}"

    # ── Mind Maps ───────────────────────────────────────────────────────

    def create_mind_map(self, topic: str) -> str:
        """Create a text-based ASCII mind map.

        Args:
            topic: The central topic for the mind map.

        Returns:
            An ASCII art mind map string.
        """
        if not self.ai:
            return "Configure AI to generate mind maps."

        prompt = f"""Create a text-based mind map for: {topic}

Use this format:
```
                  [Central Topic]
                       |
        +--------------+--------------+
        |              |              |
   [Branch 1]     [Branch 2]     [Branch 3]
        |              |              |
   Sub-topic     Sub-topic     Sub-topic
   Sub-topic     Sub-topic     Sub-topic
```

Make it comprehensive with 3-5 main branches and 2-4 sub-topics each.
Use clean ASCII art. Center the main topic."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error creating mind map: {e}"

    def create_study_guide(self, topic: str) -> str:
        """Create a structured study guide for a topic.

        Args:
            topic: The topic to create a study guide for.

        Returns:
            A formatted study guide string.
        """
        if not self.ai:
            return "Configure AI to create study guides."

        prompt = f"""Create a comprehensive study guide for: {topic}

Include:
1. Overview of the topic
2. Key concepts (with definitions)
3. Important formulas or rules (if applicable)
4. Common exam questions and answers
5. Tips for remembering the material
6. Practice problems or questions

Format as a clear, organized study guide that a student can use to prepare for a test."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error creating study guide: {e}"

    # ── Step-by-Step Guides ─────────────────────────────────────────────

    def how_to(self, task: str) -> str:
        """Create a step-by-step guide for completing a task.

        Args:
            task: The task to explain.

        Returns:
            A step-by-step guide string.
        """
        if not self.ai:
            return "Configure AI to create guides."

        prompt = f"""Create a clear, step-by-step guide for: {task}

Format as:
Step 1: [action]
- Details about this step

Step 2: [action]
- Details about this step

etc.

Include tips and common mistakes to avoid."""

        try:
            return self.ai.chat(prompt, mode="explain")
        except Exception as e:
            return f"Error creating guide: {e}"

    def prereq_checklist(self, topic: str) -> List[str]:
        """Generate a prerequisite knowledge checklist for a topic.

        Args:
            topic: The topic to check prerequisites for.

        Returns:
            A list of prerequisite topics or skills.
        """
        if not self.ai:
            return ["Configure AI for prerequisite checking."]

        prompt = f"""List the prerequisite knowledge needed to understand: {topic}

Format as a checklist:
• [prerequisite 1]
• [prerequisite 2]
• [prerequisite 3]

Order from most basic to most advanced."""

        try:
            response = self.ai.chat(prompt, mode="explain")
            return [
                line.strip().lstrip("•- ")
                for line in response.split("\n")
                if line.strip() and line.strip()[0] in "•-"
            ]
        except Exception as e:
            return [f"Error: {e}"]

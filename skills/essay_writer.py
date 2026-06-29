"""Essay writer with outlining, drafting, and citations.

Provides a complete essay writing pipeline: generate structured outlines,
write full drafts from outlines, add in-text citations in various academic
formats (APA, MLA, Chicago, Harvard), improve drafts based on feedback,
and export to multiple file formats.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class Outline:
    """Structured essay outline.

    Attributes:
        topic: The essay topic or title.
        thesis: The thesis statement.
        sections: A list of section dicts, each with 'heading' and 'points' keys.
    """

    topic: str
    thesis: str = ""
    sections: List[Dict] = field(default_factory=list)

    def format_terminal(self) -> str:
        """Format the outline for terminal display with Rich markup.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [f"[bold cyan]Topic:[/] {self.topic}", ""]
        if self.thesis:
            lines.append(f"[bold magenta]Thesis:[/] {self.thesis}")
            lines.append("")
        for i, section in enumerate(self.sections, 1):
            lines.append(f"[bold yellow]{i}. {section['heading']}[/]")
            for point in section.get("points", []):
                lines.append(f"   • {point}")
            lines.append("")
        return "\n".join(lines)

    def format_plain(self) -> str:
        """Format the outline as plain text without Rich markup.

        Returns:
            A plain-text multi-line string.
        """
        lines = [f"Topic: {self.topic}", ""]
        if self.thesis:
            lines.append(f"Thesis: {self.thesis}")
            lines.append("")
        for i, section in enumerate(self.sections, 1):
            lines.append(f"{i}. {section['heading']}")
            for point in section.get("points", []):
                lines.append(f"   - {point}")
            lines.append("")
        return "\n".join(lines)


@dataclass
class Essay:
    """A complete essay with metadata.

    Attributes:
        title: The essay title.
        content: The full essay text.
        word_count: Approximate word count.
        citations: List of citation strings.
        style: The essay style (argumentative, expository, etc.).
    """

    title: str = ""
    content: str = ""
    word_count: int = 0
    citations: List[str] = field(default_factory=list)
    style: str = ""

    def format_terminal(self) -> str:
        """Format the essay for terminal display.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [
            f"[bold cyan]{'=' * 60}[/]",
            f"[bold white]{self.title or 'Untitled Essay'}[/]",
            f"[dim]Word count: ~{self.word_count} | Style: {self.style}[/]",
            f"[bold cyan]{'=' * 60}[/]",
            "",
        ]
        # Render content with paragraph spacing
        paragraphs = self.content.split("\n\n")
        for para in paragraphs:
            if para.strip():
                lines.append(para.strip())
                lines.append("")

        if self.citations:
            lines.append(f"[bold cyan]{'=' * 60}[/]")
            lines.append("[bold yellow]References[/]")
            for cite in self.citations:
                lines.append(f"  {cite}")

        return "\n".join(lines)


# ── EssayWriter ──────────────────────────────────────────────────────────────


class EssayWriter:
    """Helps write essays from outline to final draft.

    Supports the full essay writing pipeline: outline generation,
    draft writing, citation addition, improvement, and export.

    Args:
        ai_engine: An AI engine instance that provides ``chat()``.
    """

    CITATION_STYLES: Dict[str, str] = {
        "apa": "APA (Author, Year)",
        "mla": "MLA (Author Page)",
        "chicago": "Chicago (Footnotes)",
        "harvard": "Harvard (Author, Year)",
    }

    ESSAY_STYLES: List[str] = [
        "argumentative",
        "expository",
        "narrative",
        "descriptive",
        "persuasive",
        "compare_contrast",
        "analytical",
        "cause_effect",
    ]

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Outline Generation ──────────────────────────────────────────────

    def create_outline(
        self,
        topic: str,
        length: str = "500 words",
        style: str = "argumentative",
        num_sections: int = 4,
    ) -> Outline:
        """Generate a structured essay outline.

        Uses the AI engine to create a detailed outline with thesis
        statement and section breakdowns.

        Args:
            topic: The essay topic or prompt.
            length: Target length (e.g. '500 words', '3 pages').
            style: Essay style (argumentative, expository, narrative, etc.).
            num_sections: Approximate number of body sections desired.

        Returns:
            An ``Outline`` object with thesis and sections.
        """
        if not self.ai:
            return Outline(
                topic=topic,
                thesis="Configure AI for full outline generation",
                sections=[
                    {
                        "heading": "Introduction",
                        "points": ["Add your API key to generate full outlines"],
                    }
                ],
            )

        prompt = f"""Create a detailed essay outline for: "{topic}"
Essay type: {style}
Target length: {length}
Number of sections: {num_sections}

Format your response EXACTLY as:
THESIS: [thesis statement]

1. [Section heading]
   - [point 1]
   - [point 2]
   - [point 3]

2. [Section heading]
   - [point 1]
   - [point 2]

(etc.)"""

        try:
            response = self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return Outline(
                topic=topic,
                thesis=f"Error generating outline: {e}",
                sections=[],
            )

        return self._parse_outline(topic, response)

    def _parse_outline(self, topic: str, text: str) -> Outline:
        """Parse an outline from AI response text.

        Args:
            topic: The original essay topic.
            text: The AI-generated outline text.

        Returns:
            An ``Outline`` object.
        """
        outline = Outline(topic=topic)
        lines = text.split("\n")
        current_section: Optional[Dict] = None

        for line in lines:
            line = line.strip()
            if line.upper().startswith("THESIS:"):
                outline.thesis = line.split(":", 1)[1].strip()
            elif re.match(r"^\d+\.\s", line):
                if current_section:
                    outline.sections.append(current_section)
                heading = re.sub(r"^\d+\.\s*", "", line)
                current_section = {"heading": heading, "points": []}
            elif line.startswith("-") or line.startswith("•"):
                if current_section is not None:
                    point = line.lstrip("-• ").strip()
                    if point:
                        current_section["points"].append(point)

        if current_section:
            outline.sections.append(current_section)

        return outline

    # ── Draft Writing ───────────────────────────────────────────────────

    def write_draft(
        self,
        outline: Outline,
        word_count: int = 500,
        tone: str = "academic",
    ) -> str:
        """Write a full essay draft from an outline.

        Args:
            outline: The ``Outline`` to base the essay on.
            word_count: Target word count.
            tone: Writing tone (academic, casual, formal).

        Returns:
            The complete essay text.
        """
        if not self.ai:
            return "Configure AI to generate essay drafts."

        outline_text = outline.format_plain()
        prompt = f"""Write a complete {word_count}-word essay based on this outline:

{outline_text}

Write the full essay with:
- Engaging introduction with thesis statement
- Well-developed body paragraphs with evidence and examples
- Strong conclusion that reinforces the thesis
- Smooth transitions between paragraphs
- Tone: {tone}

Write the essay now:"""

        try:
            return self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return f"Error writing draft: {e}"

    def write_draft_from_topic(
        self,
        topic: str,
        word_count: int = 500,
        style: str = "argumentative",
        tone: str = "academic",
    ) -> str:
        """Write a full essay draft directly from a topic (no outline needed).

        Args:
            topic: The essay topic or prompt.
            word_count: Target word count.
            style: Essay style.
            tone: Writing tone.

        Returns:
            The complete essay text.
        """
        if not self.ai:
            return "Configure AI to generate essay drafts."

        prompt = f"""Write a complete {word_count}-word {style} essay on this topic:

"{topic}"

Write the full essay with:
- Engaging introduction with clear thesis statement
- Well-developed body paragraphs with evidence and examples
- Strong conclusion
- Smooth transitions
- Tone: {tone}

Write the essay now:"""

        try:
            return self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return f"Error writing draft: {e}"

    # ── Citations ───────────────────────────────────────────────────────

    def add_citations(
        self,
        draft: str,
        sources: Optional[List[str]] = None,
        style: str = "apa",
    ) -> str:
        """Add properly formatted citations to an essay draft.

        Uses the AI engine to insert in-text citations and generate
        a references section.

        Args:
            draft: The essay text to add citations to.
            sources: Optional list of source strings (title, author, year).
            style: Citation style — 'apa', 'mla', 'chicago', or 'harvard'.

        Returns:
            The essay with citations added.
        """
        if not self.ai:
            return draft

        style_name = self.CITATION_STYLES.get(style.lower(), "APA")
        sources_str = (
            "Use these sources: " + "; ".join(sources)
            if sources
            else "Create realistic citations for the claims made."
        )

        prompt = f"""Add proper {style_name} in-text citations to this essay.
{sources_str}

Also add a {'References' if style.lower() in ('apa', 'harvard') else 'Works Cited' if style.lower() == 'mla' else 'Bibliography'} section at the end.

Format all citations correctly in {style_name} style.

Essay:
{draft}"""

        try:
            return self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return f"Error adding citations: {e}\n\n{draft}"

    # ── Improvement ─────────────────────────────────────────────────────

    def improve(self, draft: str, feedback: str = "") -> str:
        """Improve an essay draft based on optional feedback.

        Args:
            draft: The current essay text.
            feedback: Specific areas to focus on (optional).

        Returns:
            The improved essay text.
        """
        if not self.ai:
            return draft

        focus_text = f"\nFocus on: {feedback}" if feedback else ""
        prompt = f"""Improve this essay. Make it more polished, clearer, and more compelling.
Fix grammar, improve vocabulary, strengthen arguments, and enhance flow.
{focus_text}

Return the complete improved essay:

{draft}"""

        try:
            return self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return f"Error improving essay: {e}\n\n{draft}"

    def expand_section(self, draft: str, section_hint: str, extra_words: int = 100) -> str:
        """Expand a specific section of an essay with more detail.

        Args:
            draft: The full essay text.
            section_hint: Keywords identifying the section to expand.
            extra_words: Approximate number of additional words.

        Returns:
            The essay with the expanded section.
        """
        if not self.ai:
            return draft

        prompt = f"""Expand the section about "{section_hint}" in this essay by approximately {extra_words} words. Add more detail, evidence, and analysis.

Return the COMPLETE essay with the expanded section:

{draft}"""

        try:
            return self.ai.chat(prompt, mode="essay")
        except Exception as e:
            return f"Error expanding section: {e}\n\n{draft}"

    # ── Export ──────────────────────────────────────────────────────────

    def export(self, essay: str, filepath: str, fmt: str = "txt") -> str:
        """Export an essay to a file.

        Args:
            essay: The essay text.
            filepath: Path to write the file to.
            fmt: Export format — 'txt', 'md', or 'html'.

        Returns:
            The file path written.
        """
        if fmt == "md":
            content = f"# Essay\n\n{essay}"
        elif fmt == "html":
            # Simple HTML wrapper
            title = essay.split("\n")[0][:80] if essay else "Essay"
            escaped = (
                essay.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            paragraphs = "\n".join(
                f"<p>{p.strip()}</p>"
                for p in escaped.split("\n\n")
                if p.strip()
            )
            content = (
                f"<!DOCTYPE html>\n"
                f"<html>\n<head>\n"
                f'<meta charset="utf-8">\n'
                f"<title>{title}</title>\n"
                f"<style>body{{max-width:800px;margin:40px auto;"
                f"font-family:Georgia,serif;line-height:1.6;"
                f"padding:0 20px;}}</style>\n"
                f"</head>\n<body>\n{paragraphs}\n</body>\n</html>"
            )
        else:
            # Plain text
            content = essay

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def get_word_count(self, text: str) -> int:
        """Get an approximate word count of a text.

        Args:
            text: The text to count words in.

        Returns:
            The word count.
        """
        return len(text.split())

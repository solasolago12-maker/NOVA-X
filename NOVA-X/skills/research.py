"""Research assistant with web search and source management.

Provides web search via DuckDuckGo, deep research synthesis using AI,
bibliography generation in multiple academic formats, and source
management for academic work.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ── Data Classes ─────────────────────────────────────────────────────────────


@dataclass
class SearchResult:
    """A single web search result.

    Attributes:
        title: The page title.
        url: The page URL.
        snippet: A text snippet from the page.
        source: The domain name extracted from the URL.
    """

    title: str
    url: str
    snippet: str
    source: str = ""

    def format_terminal(self) -> str:
        """Format the search result for terminal display.

        Returns:
            A string with Rich formatting tags.
        """
        return (
            f"[bold cyan]{self.title}[/]\n"
            f"[dim]{self.url}[/]\n"
            f"{self.snippet[:200]}"
        )

    def format_plain(self) -> str:
        """Format the search result as plain text.

        Returns:
            A plain-text string.
        """
        return f"{self.title}\n{self.url}\n{self.snippet[:200]}"


@dataclass
class ResearchReport:
    """A compiled research report.

    Attributes:
        topic: The research topic.
        summary: A comprehensive summary.
        key_points: List of key findings.
        sources: List of source dicts with 'title' and 'url' keys.
        conclusion: Optional conclusion text.
    """

    topic: str
    summary: str = ""
    key_points: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    conclusion: str = ""

    def format_terminal(self) -> str:
        """Format the report for terminal display with Rich markup.

        Returns:
            A multi-line string with Rich formatting tags.
        """
        lines = [
            f"[bold cyan]{'=' * 60}[/]",
            f"[bold white]Research: {self.topic}[/]",
            f"[bold cyan]{'=' * 60}[/]",
            "",
            f"[bold green]Summary:[/]\n{self.summary}\n",
        ]

        if self.key_points:
            lines.append("[bold yellow]Key Points:[/]")
            for point in self.key_points:
                lines.append(f"  • {point}")
            lines.append("")

        if self.conclusion:
            lines.append(f"[bold magenta]Conclusion:[/]\n{self.conclusion}\n")

        if self.sources:
            lines.append("[bold cyan]Sources:[/]")
            for s in self.sources:
                lines.append(
                    f"  • {s.get('title', 'Unknown')} - "
                    f"[dim]{s.get('url', '')}[/]"
                )

        return "\n".join(lines)

    def format_plain(self) -> str:
        """Format the report as plain text.

        Returns:
            A plain-text multi-line string.
        """
        lines = [
            f"{'=' * 60}",
            f"Research: {self.topic}",
            f"{'=' * 60}",
            "",
            f"Summary:\n{self.summary}\n",
        ]

        if self.key_points:
            lines.append("Key Points:")
            for point in self.key_points:
                lines.append(f"  - {point}")
            lines.append("")

        if self.conclusion:
            lines.append(f"Conclusion:\n{self.conclusion}\n")

        if self.sources:
            lines.append("Sources:")
            for s in self.sources:
                lines.append(f"  - {s.get('title', 'Unknown')} - {s.get('url', '')}")

        return "\n".join(lines)


# ── ResearchAssistant ────────────────────────────────────────────────────────


class ResearchAssistant:
    """Helps with research, web search, and source management.

    Provides web search via DuckDuckGo, AI-powered research synthesis,
    bibliography generation, and source organization.

    Args:
        ai_engine: An AI engine instance that provides ``chat()``.
    """

    def __init__(self, ai_engine=None) -> None:
        self.ai = ai_engine

    # ── Web Search ──────────────────────────────────────────────────────

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Search the web using DuckDuckGo.

        Args:
            query: The search query string.
            num_results: Maximum number of results to return.

        Returns:
            A list of ``SearchResult`` objects.
        """
        try:
            from duckduckgo_search import DDGS

            results: List[SearchResult] = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    url = r.get("href", "")
                    # Extract domain as source
                    source = ""
                    if url:
                        parts = url.split("/")
                        if len(parts) >= 3:
                            source = parts[2]

                    results.append(
                        SearchResult(
                            title=r.get("title", ""),
                            url=url,
                            snippet=r.get("body", ""),
                            source=source,
                        )
                    )
            return results
        except ImportError:
            return [
                SearchResult(
                    title="DuckDuckGo search not available",
                    url="",
                    snippet=(
                        "Install duckduckgo-search: "
                        "pip install duckduckgo-search"
                    ),
                )
            ]
        except Exception as e:
            return [
                SearchResult(
                    title="Search error",
                    url="",
                    snippet=str(e),
                )
            ]

    # ── Deep Research ───────────────────────────────────────────────────

    def deep_research(self, topic: str, num_sources: int = 8) -> ResearchReport:
        """Conduct deep research on a topic.

        Searches the web and uses AI to synthesize findings into
        a comprehensive research report.

        Args:
            topic: The research topic.
            num_sources: Number of web sources to gather.

        Returns:
            A ``ResearchReport`` with summary, key points, and sources.
        """
        report = ResearchReport(topic=topic)

        # Search for information
        search_results = self.search(topic, num_results=num_sources)
        report.sources = [
            {"title": r.title, "url": r.url} for r in search_results if r.url
        ]

        # Use AI to synthesize
        if self.ai:
            search_text = "\n\n".join(
                [
                    f"Source: {r.title}\n{r.snippet}"
                    for r in search_results[:5]
                    if r.snippet
                ]
            )

            prompt = f"""Research and summarize this topic comprehensively: {topic}

Here are search results to base your research on:
{search_text}

Provide:
1. A comprehensive summary (3-5 paragraphs)
2. 5-7 key bullet points
3. A brief conclusion

Format as:
SUMMARY:
[summary]

KEY POINTS:
• [point 1]
• [point 2]
...

CONCLUSION:
[conclusion]"""

            try:
                response = self.ai.chat(prompt, mode="research")
            except Exception as e:
                report.summary = f"Error during AI synthesis: {e}"
                return report

            # Parse response
            summary = ""
            points: List[str] = []
            conclusion = ""

            if "SUMMARY:" in response:
                # Split on KEY POINTS
                parts = response.split("KEY POINTS:")
                summary = parts[0].replace("SUMMARY:", "").strip()

                if len(parts) > 1:
                    rest = parts[1]

                    # Split on CONCLUSION
                    if "CONCLUSION:" in rest:
                        points_text, conclusion_text = rest.split(
                        "CONCLUSION:", 1)
                        conclusion = conclusion_text.strip()
                    else:
                        points_text = rest

                    # Extract bullet points
                    for line in points_text.split("\n"):
                        line = line.strip()
                        if line and line[0] in "•-":
                            points.append(line.lstrip("•- ").strip())
                        elif line and line[0].isdigit() and "." in line[:3]:
                            # Handle "1. Point" format
                            points.append(line.split(".", 1)[1].strip())
            else:
                # No structured format, use whole response as summary
                summary = response

            report.summary = summary
            report.key_points = points
            report.conclusion = conclusion
        else:
            report.summary = "Configure AI for deep research synthesis."

        return report

    # ── Summarization ───────────────────────────────────────────────────

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        """Summarize a long text or article.

        Args:
            text: The text to summarize.
            max_sentences: Maximum number of sentences in the summary.

        Returns:
            A concise summary.
        """
        if not self.ai:
            return "Configure AI for summarization."

        prompt = f"""Summarize the following text in {max_sentences} sentences or fewer:

{text[:5000]}

Provide a concise summary capturing the main points."""

        try:
            return self.ai.chat(prompt, mode="research")
        except Exception as e:
            return f"Error summarizing: {e}"

    def summarize_url(self, url: str) -> str:
        """Fetch and summarize a web page.

        Args:
            url: The URL to summarize.

        Returns:
            A summary of the page content.
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Extract text
            text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = "\n".join(lines)

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "..."

            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else url

            if self.ai:
                prompt = f"""Summarize this web page titled "{title_text}":

{text[:5000]}

Provide a concise summary of the key points."""
                return self.ai.chat(prompt, mode="research")
            else:
                return f"Title: {title_text}\n\n{text[:1000]}..."

        except ImportError:
            return "Install requests and beautifulsoup4 to summarize URLs."
        except Exception as e:
            return f"Error fetching/summarizing URL: {e}"

    # ── Bibliography ────────────────────────────────────────────────────

    def generate_bibliography(
        self, sources: List[Dict], style: str = "apa"
    ) -> str:
        """Generate a formatted bibliography/works cited.

        Args:
            sources: List of source dicts with 'title' and 'url' keys.
            style: Citation style — 'apa', 'mla', 'chicago', or 'harvard'.

        Returns:
            A formatted bibliography string.
        """
        if not self.ai:
            # Generate a basic bibliography without AI
            lines = []
            header = {
                "apa": "References",
                "mla": "Works Cited",
                "chicago": "Bibliography",
                "harvard": "References",
            }.get(style.lower(), "References")
            lines.append(header)
            lines.append("")

            for i, s in enumerate(sources, 1):
                title = s.get("title", "Unknown")
                url = s.get("url", "")
                lines.append(f"{i}. {title}. {url}")

            return "\n".join(lines)

        sources_text = "\n".join(
            [
                f"- {s.get('title', '')}: {s.get('url', '')}"
                for s in sources
            ]
        )

        prompt = f"""Format these sources as a {style.upper()} bibliography:

{sources_text}

Provide ONLY the formatted bibliography, no extra text."""

        try:
            return self.ai.chat(prompt, mode="research")
        except Exception as e:
            return f"Error generating bibliography: {e}"

    # ── Source Management ───────────────────────────────────────────────

    def save_sources(
        self, sources: List[Dict], filepath: str
    ) -> None:
        """Save sources to a JSON file for later use.

        Args:
            sources: List of source dicts.
            filepath: Path to write the JSON file.
        """
        import json

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sources, f, indent=2, ensure_ascii=False)

    def load_sources(self, filepath: str) -> List[Dict]:
        """Load sources from a JSON file.

        Args:
            filepath: Path to the JSON file.

        Returns:
            A list of source dicts.
        """
        import json

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def quick_fact(self, query: str) -> str:
        """Get a quick fact or answer about a topic.

        Uses web search and AI to provide a concise answer.

        Args:
            query: The factual question.

        Returns:
            A concise answer.
        """
        # Search for quick info
        results = self.search(query, num_results=3)

        if self.ai:
            search_text = "\n".join(
                [f"{r.title}: {r.snippet}" for r in results if r.snippet]
            )

            prompt = f"""Answer this question concisely based on the search results:

Question: {query}

Search results:
{search_text}

Provide a brief, accurate answer in 2-3 sentences."""

            try:
                return self.ai.chat(prompt, mode="research")
            except Exception as e:
                return f"Error: {e}"

        # Fallback: return best snippet
        for r in results:
            if r.snippet:
                return r.snippet

        return "No results found."

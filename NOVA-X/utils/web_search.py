"""Web search utilities for NOVA-X.

Provides DuckDuckGo-powered web search and news search with structured
result formatting. Gracefully degrades when the optional dependency is
unavailable.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchResult:
    """A single web search result."""

    title: str
    url: str
    snippet: str
    source: str = "web"

    def __str__(self) -> str:
        return f"{self.title}\n  {self.url}\n  {self.snippet[:200]}"


class WebSearch:
    """DuckDuckGo-based web search client.

    Requires the ``duckduckgo-search`` package. If it is not installed,
    searches will return an empty list with a warning message.
    """

    def __init__(self) -> None:
        """Attempt to import DuckDuckGo search."""
        try:
            from duckduckgo_search import DDGS
            self._ddgs_class = DDGS
            self._available = True
        except ImportError:
            self._ddgs_class = None
            self._available = False

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Perform a web search.

        Args:
            query: Search query string.
            num_results: Maximum number of results (1-10).

        Returns:
            List of :class:`SearchResult` objects.
        """
        if not self._available:
            print("[WARNING] duckduckgo-search not installed. Run: pip install duckduckgo-search")
            return []
        results: List[SearchResult] = []
        try:
            with self._ddgs_class() as ddgs:
                for r in ddgs.text(query, max_results=min(num_results, 10)):
                    results.append(SearchResult(
                        title=r.get("title", "Untitled"),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        source="web",
                    ))
        except Exception as exc:
            print(f"[ERROR] Web search failed: {exc}")
        return results

    def search_news(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """Search for news articles.

        Args:
            query: Search query string.
            num_results: Maximum number of results (1-10).

        Returns:
            List of :class:`SearchResult` objects with ``source="news"``.
        """
        if not self._available:
            print("[WARNING] duckduckgo-search not installed.")
            return []
        results: List[SearchResult] = []
        try:
            with self._ddgs_class() as ddgs:
                for r in ddgs.news(query, max_results=min(num_results, 10)):
                    results.append(SearchResult(
                        title=r.get("title", "Untitled"),
                        url=r.get("url", ""),
                        snippet=r.get("body", ""),
                        source="news",
                    ))
        except Exception as exc:
            print(f"[ERROR] News search failed: {exc}")
        return results

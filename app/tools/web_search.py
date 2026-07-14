"""Free, no-API-key web search tool (DuckDuckGo) exposed as a plain
Python function so AutoGen agents can call it."""

from duckduckgo_search import DDGS
from app.config import MAX_SEARCH_RESULTS


def web_search(query: str, max_results: int = MAX_SEARCH_RESULTS) -> str:
    """Search the web and return a compact, citable summary of results.

    Args:
        query: Search query string.
        max_results: Number of results to fetch.

    Returns:
        A formatted string with title, snippet, and URL per result.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"[web_search error] Could not fetch results for '{query}': {e}"

    if not results:
        return f"[web_search] No results found for '{query}'."

    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        body = r.get("body", "")
        href = r.get("href", "")
        formatted.append(f"{i}. {title}\n   {body}\n   Source: {href}")

    return f"Search results for '{query}':\n\n" + "\n\n".join(formatted)

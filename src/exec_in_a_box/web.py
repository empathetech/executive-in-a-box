"""Web content fetcher.

Fetches web pages and strips them to readable plain text for injection
into LLM prompts. Fetched content is treated as untrusted data.

Reference: hacky-hours/02-design/decisions/2026-03-21-web-content-fetching.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

# Max content length to inject into a prompt (characters).
# ~8000 chars is roughly ~2000 tokens — enough for useful context
# without blowing up the context window.
DEFAULT_MAX_LENGTH = 8000

# Regex to detect URLs in user input
URL_PATTERN = re.compile(
    r"(?:@url\s+)?(https?://[^\s<>\"]+)",
    re.IGNORECASE,
)


@dataclass
class FetchResult:
    """Result of fetching a URL."""

    url: str
    text: str
    title: str | None
    truncated: bool
    error: str | None


def extract_urls(text: str) -> list[str]:
    """Extract URLs from user input.

    Supports bare URLs and @url prefix syntax.
    """
    return URL_PATTERN.findall(text)


def fetch_url(
    url: str, max_length: int = DEFAULT_MAX_LENGTH
) -> FetchResult:
    """Fetch a URL and return its content as plain text.

    Uses plain HTTP (no JavaScript rendering). Sites that
    require JS will return limited or no content.
    """
    try:
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=15.0,
            headers={
                "User-Agent": (
                    "executive-in-a-box/0.2.0 "
                    "(strategic advisor tool)"
                ),
            },
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        return FetchResult(
            url=url,
            text="",
            title=None,
            truncated=False,
            error="Request timed out. The site may be slow or blocking automated requests.",
        )
    except httpx.HTTPStatusError as e:
        return FetchResult(
            url=url,
            text="",
            title=None,
            truncated=False,
            error=f"HTTP {e.response.status_code}. The page couldn't be loaded.",
        )
    except httpx.RequestError:
        return FetchResult(
            url=url,
            text="",
            title=None,
            truncated=False,
            error="Couldn't reach the URL. Check that it's correct and you're online.",
        )

    # Parse HTML and extract text
    soup = BeautifulSoup(response.text, "html.parser")

    # Get title
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Remove script, style, nav, footer, header elements
    for tag in soup(
        ["script", "style", "nav", "footer", "header", "aside"]
    ):
        tag.decompose()

    # Get text content
    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Truncate if needed
    truncated = len(text) > max_length
    if truncated:
        text = text[:max_length] + "\n\n[Content truncated]"

    return FetchResult(
        url=url,
        text=text,
        title=title,
        truncated=truncated,
        error=None,
    )


def fetch_urls_for_context(
    urls: list[str],
) -> str:
    """Fetch multiple URLs and format them for prompt injection.

    Returns a formatted string ready to include in the prompt
    as a USER DOCUMENT section.
    """
    if not urls:
        return ""

    parts = []
    for url in urls:
        result = fetch_url(url)
        if result.error:
            parts.append(
                f"[FETCH FAILED: {url}]\n{result.error}"
            )
        else:
            header = f"[WEB CONTENT: {url}]"
            if result.title:
                header += f"\nTitle: {result.title}"
            if result.truncated:
                header += "\n(Content was truncated to fit)"
            parts.append(f"{header}\n\n{result.text}")

    return "\n\n---\n\n".join(parts)

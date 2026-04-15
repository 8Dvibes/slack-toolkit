"""Documentation fetcher for slack-cli.

Fetches and caches Slack API method documentation from docs.slack.dev.
Cache lives at ~/.slack-cli/docs/<method>.md with 30-day TTL.
"""

import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

DOCS_BASE = "https://docs.slack.dev/reference/methods/"
DOCS_CACHE_DIR = Path.home() / ".slack-cli" / "docs"
CACHE_TTL_DAYS = 30
CACHE_TTL_SECONDS = CACHE_TTL_DAYS * 86400


def _cache_path(method_name: str) -> Path:
    """Return the cache file path for a method."""
    safe_name = method_name.replace("/", "_")
    return DOCS_CACHE_DIR / f"{safe_name}.md"


def _is_cache_fresh(cache_file: Path) -> bool:
    """Check if cached file is within TTL."""
    if not cache_file.exists():
        return False
    age = time.time() - cache_file.stat().st_mtime
    return age < CACHE_TTL_SECONDS


def _fetch_url(url: str) -> str:
    """Fetch a URL and return the response body as text."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "slack-cli/0.2.0 (docs fetcher)"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ""
        raise
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        return ""


def _strip_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return text.strip()


def _parse_method_doc(html_content: str, method_name: str) -> str:
    """Parse the HTML and extract useful documentation as Markdown."""
    if not html_content:
        return f"# {method_name}\n\nDocumentation not available.\n"

    lines = [f"# {method_name}", ""]

    # Extract description - look for meta description or first meaningful paragraph
    desc_match = re.search(
        r'<meta name="description" content="([^"]+)"', html_content
    )
    if desc_match:
        lines.append(_strip_html_tags(desc_match.group(1)))
        lines.append("")

    # Extract doc URL
    lines.append(f"**Docs:** {DOCS_BASE}{method_name}/")
    lines.append("")

    # Look for parameter tables
    # Try to find section headings and their content
    sections = re.findall(
        r"<h[23][^>]*>(.*?)</h[23]>(.*?)(?=<h[23]|$)",
        html_content,
        re.DOTALL | re.IGNORECASE,
    )

    for heading_raw, content_raw in sections:
        heading = _strip_html_tags(heading_raw).strip()
        if not heading:
            continue

        # Skip navigation-ish sections
        if heading.lower() in ("on this page", "table of contents", "contents"):
            continue

        lines.append(f"## {heading}")
        lines.append("")

        # Extract table rows if present
        table_rows = re.findall(
            r"<tr[^>]*>(.*?)</tr>", content_raw, re.DOTALL | re.IGNORECASE
        )
        if table_rows:
            for row in table_rows:
                cells = re.findall(
                    r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL | re.IGNORECASE
                )
                if cells:
                    cell_texts = [_strip_html_tags(c).replace("\n", " ").strip() for c in cells]
                    if any(cell_texts):
                        lines.append("| " + " | ".join(cell_texts) + " |")
            lines.append("")
        else:
            # Extract paragraphs and list items
            paragraphs = re.findall(
                r"<p[^>]*>(.*?)</p>", content_raw, re.DOTALL | re.IGNORECASE
            )
            list_items = re.findall(
                r"<li[^>]*>(.*?)</li>", content_raw, re.DOTALL | re.IGNORECASE
            )

            for p in paragraphs:
                text = _strip_html_tags(p).strip()
                if text and len(text) > 5:
                    lines.append(text)
                    lines.append("")

            for li in list_items:
                text = _strip_html_tags(li).strip()
                if text and len(text) > 2:
                    lines.append(f"- {text}")
            if list_items:
                lines.append("")

    # If we didn't extract much, do a simpler extraction
    if len(lines) < 6:
        # Try code blocks (error codes, response examples)
        code_blocks = re.findall(
            r"<code[^>]*>(.*?)</code>", html_content, re.DOTALL | re.IGNORECASE
        )
        if code_blocks:
            lines.append("## Code Examples")
            lines.append("")
            for block in code_blocks[:5]:
                text = _strip_html_tags(block).strip()
                if text and len(text) > 3:
                    lines.append(f"`{text}`")
            lines.append("")

    # Add cache metadata
    lines.append("---")
    lines.append(f"*Cached: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}*")
    lines.append(f"*Source: {DOCS_BASE}{method_name}/*")

    return "\n".join(lines)


def fetch_method_doc(
    method_name: str,
    fresh: bool = False,
) -> str:
    """Fetch documentation for a Slack API method.

    Checks cache first (30-day TTL). Fetches from docs.slack.dev if stale or missing.

    Args:
        method_name: Method name (e.g. "conversations.open")
        fresh: If True, bypass cache and fetch live

    Returns:
        Markdown string with the method documentation.
    """
    DOCS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_path(method_name)

    # Check cache
    if not fresh and _is_cache_fresh(cache_file):
        return cache_file.read_text()

    # Fetch from docs.slack.dev
    url = f"{DOCS_BASE}{method_name}/"
    print(f"Fetching docs for {method_name}...", file=sys.stderr)
    html_content = _fetch_url(url)

    if not html_content:
        # Try without trailing slash
        url = f"{DOCS_BASE}{method_name}"
        html_content = _fetch_url(url)

    doc_text = _parse_method_doc(html_content, method_name)

    # Write to cache
    cache_file.write_text(doc_text)
    return doc_text


def cmd_docs(method_name: str, fresh: bool = False, as_json: bool = False) -> None:
    """Show documentation for a Slack API method."""
    doc = fetch_method_doc(method_name, fresh=fresh)

    if as_json:
        cache_file = _cache_path(method_name)
        result = {
            "method": method_name,
            "doc_url": f"{DOCS_BASE}{method_name}/",
            "cached": str(cache_file),
            "content": doc,
        }
        print(json.dumps(result, indent=2))
    else:
        print(doc)

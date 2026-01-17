"""Web scraping tools for agents (non-Temporal versions)."""

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md


async def get_page_content(url: str) -> str:
    """
    Fetch and convert a web page to markdown.

    This is a standalone function (not a Temporal activity) that can be used
    directly by agents running within activities.

    Args:
        url: The URL to fetch

    Returns:
        Markdown content of the page
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                    )
                },
            )
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Convert to markdown
            markdown_content = md(str(soup), heading_style="ATX")

            # Clean up excessive whitespace
            lines = [line.strip() for line in markdown_content.split("\n")]
            cleaned = "\n".join(line for line in lines if line)

            return cleaned

        except Exception as e:
            return f"Error fetching {url}: {str(e)}"

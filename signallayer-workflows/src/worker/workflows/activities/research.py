from datetime import timedelta

import inject
from temporalio import activity

from src.common.clients.reddit import (
    RedditClient,
    RedditCommunityPost,
    RedditSearchResult,
)
from src.worker.lib.decorators import configured_activity


@configured_activity(
    start_to_close_timeout=timedelta(minutes=2),
    max_retries=3,
)
async def find_subreddits(query: str) -> list[RedditCommunityPost]:
    """Find subreddits matching a query using Reddit search."""
    reddit = inject.instance(RedditClient)
    activity.logger.info(f"Finding subreddits for: {query}")
    response = reddit.list_communities(query)
    return response.body.data


@configured_activity(
    start_to_close_timeout=timedelta(minutes=2),
    max_retries=3,
)
async def get_latest_posts(subreddit: str) -> list[RedditCommunityPost]:
    """Get latest posts from a subreddit."""
    reddit = inject.instance(RedditClient)
    activity.logger.info(f"Getting latest posts from: {subreddit}")
    response = reddit.latest_community_posts(subreddit)
    return response.body.data


@configured_activity(
    start_to_close_timeout=timedelta(minutes=2),
    max_retries=3,
)
async def search_in_subreddit(query: str, subreddit: str) -> list[RedditSearchResult]:
    """Search for posts within a specific subreddit."""
    reddit = inject.instance(RedditClient)
    activity.logger.info(f"Searching in {subreddit} for: {query}")
    response = reddit.search_community(query, subreddit)
    return response.body.data


@configured_activity(
    start_to_close_timeout=timedelta(minutes=2),
    max_retries=3,
)
async def get_post_content(subreddit: str, post_id: str) -> str:
    """Get markdown content of a post."""
    reddit = inject.instance(RedditClient)
    activity.logger.info(f"Getting content for {post_id} in {subreddit}")
    return reddit.get_community_post_markdown(subreddit, post_id)


@configured_activity(
    start_to_close_timeout=timedelta(minutes=2),
    max_retries=3,
)
async def get_post_content_by_url(url: str) -> str:
    """Get markdown content from a URL."""
    import httpx
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md

    activity.logger.info(f"Fetching content from: {url}")

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
            activity.logger.error(f"Error fetching {url}: {e}")
            return f"Error fetching {url}: {str(e)}"

"""Integration tests for Reddit scraping via ScrapingBee."""

import os
import pytest
from scrapingbee import ScrapingBeeClient
from src.common.clients.reddit import RedditClient
from src.common.config.scrapingbee import ScrapingBeeSettings


def _get_reddit_client() -> RedditClient:
    """Create a Reddit client for testing."""
    try:
        sb_settings = ScrapingBeeSettings()
    except Exception:
        pytest.skip("ScrapingBeeSettings could not be initialized")

    sb_client = ScrapingBeeClient(api_key=sb_settings.api_key)
    return RedditClient(client=sb_client)


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("SCRAPING_BEE_API_KEY"), reason="SCRAPING_BEE_API_KEY not set")
async def test_list_communities_live() -> None:
    """Test listing communities."""
    client = _get_reddit_client()

    response = client.list_communities("python")

    if not response.body.data:
        pytest.warns(UserWarning, match="No communities found")
    else:
        community = response.body.data[0]
        assert community.name
        assert community.href


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("SCRAPING_BEE_API_KEY"), reason="SCRAPING_BEE_API_KEY not set")
async def test_latest_community_posts_live() -> None:
    """Test getting latest posts from a community."""
    client = _get_reddit_client()

    response = client.latest_community_posts("python")

    if not response.body.data:
        pytest.warns(UserWarning, match="No posts found in community")
    else:
        post = response.body.data[0]
        assert post.title
        assert post.href


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("SCRAPING_BEE_API_KEY"), reason="SCRAPING_BEE_API_KEY not set")
async def test_search_community_live() -> None:
    """Test searching within a community."""
    client = _get_reddit_client()

    # Search for 'jobs' in 'python' subreddit
    response = client.search_community("jobs", "python")

    # Verify results
    if response.body.data:
        post = response.body.data[0]
        assert post.title
        assert post.href


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("SCRAPING_BEE_API_KEY"), reason="SCRAPING_BEE_API_KEY not set")
async def test_get_community_post_markdown_live() -> None:
    """Test getting post markdown."""
    client = _get_reddit_client()

    # Fetch a post to get its ID/URL
    response = client.latest_community_posts("python")
    if not response.body.data:
        pytest.skip("No posts found")

    post = response.body.data[0]
    # Extract post ID from href
    parts = post.href.strip("/").split("/")
    if "comments" in parts:
        idx = parts.index("comments")
        post_id = "/".join(parts[idx:])

        markdown = client.get_community_post_markdown("python", post_id)
        assert markdown
        assert isinstance(markdown, str)
    else:
        pytest.warns(UserWarning, match=f"Could not parse post ID from href: {post.href}")

from .model import RedditSearchResult
from .model import RedditCommunityPost
from .model import RedditCommunity
from .model import ScrapingBeeReponse
import inject
from scrapingbee import ScrapingBeeClient


class RedditClient:
    """Client for interacting with Reddit via ScrapingBee."""

    @inject.params(client=ScrapingBeeClient)
    def __init__(self, client: ScrapingBeeClient):
        """Initialize Reddit client.

        Args:
            client: ScrapingBee client (injected via DI)
        """
        self.client = client
        self.base_url = "https://www.reddit.com"

    def list_communities(self, q: str) -> ScrapingBeeReponse[RedditCommunity]:
        url = f"{self.base_url}/search/?q={q}&type=communities"
        params = params = {
            "render_js": False,
            "json_response": True,
            "extract_rules": {
                "data": {
                    "selector": "div[data-testid='search-community']",
                    "type": "list",
                    "output": {
                        "name": "h2 > span[id^='search-community-title-']",
                        "summary": "p[data-testid='search-subreddit-desc-text']",
                        "href": {"selector": "a[href^='/r/']", "output": "@href"},
                        "members": {
                            "selector": "div.text-12.text-neutral-content-weak faceplate-number:nth-of-type(1)",
                            "output": "@number",
                        },
                        "online": {
                            "selector": "div.text-12.text-neutral-content-weak faceplate-number:nth-of-type(2)",
                            "output": "@number",
                        },
                    },
                }
            },
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return ScrapingBeeReponse[RedditCommunity](**response.json())

    def latest_community_posts(self, community: str) -> ScrapingBeeReponse[RedditCommunityPost]:
        url = f"{self.base_url}/{community}/"
        params = params = {
            "js_scenario": {
                "instructions": [
                    {"wait": 1000},
                    {"scroll_y": 10000},
                    {"wait": 1000},
                ]
            },
            "wait": 100,
            "json_response": True,
            "extract_rules": {
                "data": {
                    "selector": "shreddit-feed article",
                    "type": "list",
                    "output": {
                        "title": {
                            "selector": "a[slot='title']",
                        },
                        "href": {"selector": "a[slot='full-post-link']", "output": "@href"},
                        "author": {
                            "selector": "a[href^='/user/']",
                        },
                        "summary": {
                            "selector": "div[property='schema:articleBody']",
                        },
                    },
                }
            },
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return ScrapingBeeReponse[RedditCommunityPost](**response.json())

    def search_community(self, q: str, community: str) -> ScrapingBeeReponse[RedditSearchResult]:
        url = f"{self.base_url}/r/{community}/search/?q={q}"
        params = {
            "render_js": False,
            "json_response": True,
            "extract_rules": {
                "data": {
                    "selector": "div[data-testid='search-post-unit']",
                    "type": "list",
                    "output": {
                        "title": {
                            "selector": "a[data-testid='post-title']",
                        },
                        "href": {"selector": "a[data-testid='post-title']", "output": "@href"},
                    },
                }
            },
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return ScrapingBeeReponse[RedditSearchResult](**response.json())

    def get_community_post_markdown(self, community: str, post_id: str) -> str:
        return self.get_community_post_markdown_by_url(f"{self.base_url}/r/{community}/comments/{post_id}")
     

    def get_community_post_markdown_by_url(self, url: str) -> str:
        params = {
            "js_scenario": {
                "instructions": [
                    {"wait": 1000},
                    {"scroll_y": 10000},
                    {"wait": 1000},
                ]
            },
            "wait": 100,
            "return_page_markdown": True,
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.text
"""Email extractor agent for finding condo contact information."""

from datetime import timedelta

from agents import Agent
from temporalio.common import RetryPolicy
from temporalio.contrib.openai_agents.workflow import activity_as_tool

from src.worker.workflows.activities.research import get_post_content_by_url


def load_prompt(filename: str) -> str:
    """Load prompt from file."""
    path = f"src/worker/agents/prompts/{filename}"
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return """You are an expert at finding contact information for properties and condominiums.

Your task is to find official email addresses for property management,
sales offices, or general inquiries.

Guidelines:
1. Focus on official sources (property websites, management company sites)
2. Look for emails in "Contact Us" pages
3. Verify emails appear legitimate (not spam or personal emails)
4. Extract all relevant email addresses you find
5. Return ONLY the email addresses, one per line

Do NOT include:
- Personal emails from forums or reviews
- Spam or suspicious addresses
- Unrelated business emails
"""


email_extractor = Agent(
    name="Email Extractor",
    model="gpt-4-turbo-preview",
    instructions=load_prompt("email_extractor.md"),
    tools=[
        activity_as_tool(
            get_post_content_by_url,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
    ],
)

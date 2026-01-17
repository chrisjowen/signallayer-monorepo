from datetime import timedelta

from agents import Agent
from temporalio.common import RetryPolicy
from temporalio.contrib.openai_agents.workflow import activity_as_tool

from src.worker.workflows.activities.issues import (
    append_to_issue_comment,
    fetch_issue_details,
    list_issue_comments,
    mark_checklist_item_complete,
    post_github_comment,
    update_issue_comment,
)
from src.worker.workflows.activities.research import (
    find_subreddits,
    get_latest_posts,
    get_post_content,
    get_post_content_by_url,
    search_in_subreddit,
)


def load_prompt(filename: str) -> str:
    path = f"src/worker/agents/prompts/{filename}"
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."


researcher = Agent(
    name="Researcher 🕵️",
    model="gpt-4-turbo-preview",
    instructions=load_prompt("researcher.md"),
    tools=[
        activity_as_tool(
            fetch_issue_details,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            mark_checklist_item_complete,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            update_issue_comment,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            list_issue_comments,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            append_to_issue_comment,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(find_subreddits, start_to_close_timeout=timedelta(minutes=15)),
        activity_as_tool(post_github_comment, start_to_close_timeout=timedelta(minutes=15)),
        activity_as_tool(
            search_in_subreddit,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            get_latest_posts,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            get_post_content,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            get_post_content_by_url,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
    ],
)

from datetime import timedelta
from agents import Agent
from temporalio.common import RetryPolicy
from temporalio.contrib.openai_agents.workflow import activity_as_tool

from src.worker.workflows.activities.issues import (
    update_issue_comment,
    post_github_comment,
    add_issue_labels,
    remove_issue_label,
    fetch_issue_details,
    mark_checklist_item_complete,
)
from src.worker.workflows.activities.research import (
    find_subreddits, 
    get_latest_posts,
    get_post_content,
    search_in_subreddit,
)

def load_prompt(filename: str) -> str:
    path = f"src/worker/agents/prompts/{filename}"
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."

orchestrator = Agent(
    name="Paul Graham",
    model="gpt-4-turbo-preview",
    instructions=load_prompt("orchestrator.md"),
    tools=[
        # GitHub Tools
        activity_as_tool(
            fetch_issue_details,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            update_issue_comment,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            post_github_comment,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            mark_checklist_item_complete,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
             add_issue_labels,
             start_to_close_timeout=timedelta(minutes=2),
             retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
             remove_issue_label,
             start_to_close_timeout=timedelta(minutes=2),
             retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        # Reddit Tools
        activity_as_tool(find_subreddits, start_to_close_timeout=timedelta(minutes=2)),
        activity_as_tool(
            search_in_subreddit,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            get_latest_posts,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            get_post_content,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
    ],
)

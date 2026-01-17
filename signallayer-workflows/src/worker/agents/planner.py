from datetime import timedelta
from agents import Agent
from temporalio.common import RetryPolicy
from temporalio.contrib.openai_agents.workflow import activity_as_tool

from src.worker.workflows.activities.issues import (
    update_issue_comment,
    fetch_issue_details,
    list_issue_comments,
    append_to_issue_comment,
)

def load_prompt(filename: str) -> str:
    path = f"src/worker/agents/prompts/{filename}"
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."

planner = Agent(
    name="Planner 📋",
    model="gpt-4-turbo-preview",
    instructions=load_prompt("planner.md"),
    tools=[
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
            list_issue_comments,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
        activity_as_tool(
            append_to_issue_comment,
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=RetryPolicy(maximum_attempts=3),
        ),
    ],
)

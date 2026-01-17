"""Activities for demand signal detection from collaboration platforms."""

import inject
from datetime import timedelta
from temporalio import activity

from src.common.models import IssueDetails, IssueReference
from src.contexts.collaboration import CollaborationContext
from src.worker.lib.decorators import configured_activity


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
@inject.params(collaboration=CollaborationContext)
async def fetch_issues_by_label(
    repository: str, label: str, collaboration: CollaborationContext
) -> list[IssueReference]:
    """Fetch issues labeled as demand signals from collaboration platforms.

    Thin wrapper that delegates to CollaborationContext.

    Args:
        repository: Repository identifier (e.g., "owner/repo" for GitHub)
        label: Label to filter by (e.g., "check-demand")
        collaboration: Injected collaboration context

    Returns:
        List of issue references
    """
    activity.logger.info(f"Fetching issues by label '{label}' from repository '{repository}'")

    issues = await collaboration.fetch_issues_by_label(
        platform="github", repository=repository, label=label, state="open"
    )

    activity.logger.info(f"Found {len(issues)} demand signals")
    return issues


@configured_activity(
    name="fetch-issue-details",
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def fetch_issue_details(repository: str, issue_number: int) -> dict:
    """Fetch complete details for a specific issue.

    Args:
        repository: Repo owner/name
        issue_number: Issue number

    Returns:
        Complete issue details as a dictionary
    """
    collaboration = inject.instance(CollaborationContext)

    activity.logger.info(f"Fetching details for issue #{issue_number} from {repository}")

    details = await collaboration.fetch_issue_details(
        platform="github",
        repository=repository,
        issue_number=issue_number,
    )

    activity.logger.info(f"Fetched issue: {details.title}")

    # Return as dict to ensure JSON serializability for the agent
    return {
        "title": details.title,
        "body": details.body,
        "url": details.url,
        "state": details.state,
        "labels": details.labels,
        "author": details.author,
    }


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def post_github_comment(repository: str, issue_number: int, body: str) -> dict:
    """Post a comment to a GitHub issue.

    Args:
        repository: Repo owner/name
        issue_number: Issue number
        body: Markdown body

    Returns:
        Status dict including comment_id
    """
    # TODO: Find a way to use @inject.params here while keeping the tool schema generation working.
    # The agents SDK inspects the signature and fails on non-Pydantic types like CollaborationContext.
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Posting comment to {repository}#{issue_number}")
    comment_id = await collaboration.post_comment("github", repository, issue_number, body)
    return {"ok": True, "comment_id": comment_id}


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def list_issue_comments(repository: str, issue_number: int) -> list[dict]:
    """List all comments on a GitHub issue.

    Args:
        repository: Repo owner/name
        issue_number: Issue number

    Returns:
        List of comment dictionaries with 'id', 'body', 'author', 'created_at'
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Listing comments for {repository}#{issue_number}")
    return await collaboration.list_comments("github", repository, issue_number)


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def update_issue_comment(repository: str, comment_id: int, body: str) -> dict:
    """Update a GitHub issue comment.

    Args:
        repository: Repo owner/name
        comment_id: Comment ID
        body: New markdown body

    Returns:
        Status dict
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Updating comment {comment_id} in {repository}")
    await collaboration.update_comment("github", repository, comment_id, body)
    return {"ok": True}


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def add_issue_labels(repository: str, issue_number: int, labels: list[str]) -> dict:
    """Add labels to a GitHub issue.

    Args:
        repository: Repo owner/name
        issue_number: Issue number
        labels: List of labels to add

    Returns:
        Status dict
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Adding labels {labels} to {repository}#{issue_number}")
    await collaboration.add_labels("github", repository, issue_number, labels)
    return {"ok": True}


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def remove_issue_label(repository: str, issue_number: int, label: str) -> dict:
    """Remove a label from a GitHub issue.

    Args:
        repository: Repo owner/name
        issue_number: Issue number
        label: Label to remove

    Returns:
        Status dict
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Removing label {label} from {repository}#{issue_number}")
    await collaboration.remove_label("github", repository, issue_number, label)
    return {"ok": True}


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=5,
)
async def mark_checklist_item_complete(repository: str, comment_id: int, item_text: str) -> dict:
    """Marks a checklist item as complete in a GitHub comment.

    Args:
        repository: Repo owner/name
        comment_id: Comment ID
        item_text: The unique text component of the checklist item (without '[ ]')

    Returns:
        Status dict
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(
        f"Marking item '{item_text}' complete in comment {comment_id} in {repository}"
    )

    # 1. Get current comment
    body = await collaboration.get_comment("github", repository, comment_id)

    # 2. Update checklist item [ ] Item -> [x] Item
    target = f"[ ] {item_text}"
    replacement = f"[x] {item_text}"

    if target in body:
        new_body = body.replace(target, replacement)
        # 3. Update comment
        await collaboration.update_comment("github", repository, comment_id, new_body)
        return {"ok": True, "marked": True}
    else:
        activity.logger.warning(f"Checklist item '{target}' not found in comment {comment_id}")
        return {"ok": True, "marked": False}


@configured_activity(
    start_to_close_timeout=timedelta(seconds=30),
    max_retries=3,
)
async def append_to_issue_comment(repository: str, comment_id: int, body: str) -> dict:
    """Appends text to an existing GitHub issue comment.

    Useful for adding findings or progress updates without overwriting the original content.

    Args:
        repository: Repo owner/name
        comment_id: Comment ID
        body: Text to append (Markdown supported)

    Returns:
        Status dict
    """
    collaboration = inject.instance(CollaborationContext)
    activity.logger.info(f"Appending to comment {comment_id} in {repository}")

    current_body = await collaboration.get_comment("github", repository, comment_id)
    new_body = f"{current_body}\n\n{body}"

    await collaboration.update_comment("github", repository, comment_id, new_body)
    return {"ok": True}

## Context
The goal is to integrate Slack as an input and output channel for Temporal workflows. This requires a listener (Slack Bolt) and a workflow that can receive and respond to events.

## Goals
- Retrieve messages from a Slack channel.
- Trigger a Temporal workflow for each message.
- Echo the message back to the same channel from within the workflow.

## Decisions
- **Slack Bolt for Python**: Use the official Slack SDK to handle Events API.
- **Async Implementation**: Use `AsyncApp` from `slack-bolt` to align with the project's async nature.
- **Temporal Workflow**: The workflow will accept channel ID and text as input.
- **Activity for Posting**: Reusable activity to post messages to Slack using the Web Client.

## Risks / Trade-offs
- **Slack Retries**: Slack retries events if not acknowledged within 3s. The listener MUST acknowledge immediately before starting the long-running workflow.
- **Security**: Requires `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET`.

## Migration Plan
- Add required dependencies to `pyproject.toml`.
- Update `.env.example` with Slack configuration.
- Implement listener and workflow components.

# Change: Add Slack Echo Workflow

## Why
This change introduces a simple interactive loop with Slack using Temporal. It serves as a foundation for more complex Slack-based workflows, enabling the system to capture messages and respond asynchronously.

## What Changes
- **ADDED**: Slack event listener to capture messages.
- **ADDED**: `SlackEchoWorkflow` in Temporal to process captured messages.
- **ADDED**: Slack message posting activity.
- **ADDED**: Environment variables for Slack integration (tokens, signing secret).

## Impact
- Affected specs: `slack-integration`
- Affected code:
  - `src/common/clients/slack.py`
  - `src/worker/workflows/activities/slack.py`
  - `src/worker/workflows/slack_echo.py`
  - `src/web/slack.py`
  - `src/web/main.py`

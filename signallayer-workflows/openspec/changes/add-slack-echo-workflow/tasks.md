## 1. Setup and Dependencies
- [ ] 1.1 Add `slack-sdk` and `slack-bolt` to `pyproject.toml`
- [ ] 1.2 Update `.env.example` and local `.env` with `SLACK_BOT_TOKEN` and `SLACK_SIGNING_SECRET`

## 2. Shared Clients
- [ ] 2.1 Implement `SlackClient` in `src/common/clients/slack.py`

## 3. Temporal Workflow and Activities
- [ ] 3.1 Implement Slack activities in `src/worker/workflows/activities/slack.py`
- [ ] 3.2 Implement `SlackEchoWorkflow` in `src/worker/workflows/slack_echo.py`
- [ ] 3.3 Ensure the new workflow and activity are automatically registered by the worker

## 4. Slack Event Listener
- [ ] 4.1 Implement Slack event listener using `slack-bolt` in `src/web/slack.py`
- [ ] 4.2 Register the Slack listener route in `src/web/main.py`

## 5. Verification
- [ ] 5.1 Create integration test for `SlackEchoWorkflow`
- [ ] 5.2 Verify Slack events trigger the workflow locally

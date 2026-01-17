## ADDED Requirements

### Requirement: Slack Message Capture
The system SHALL listen for message events in Slack channels and capture the message text, channel ID, and user ID.

#### Scenario: Message received from Slack
- **WHEN** a user posts a message in a monitored Slack channel
- **THEN** the system acknowledges the event and extracts the message details

### Requirement: Temporal Workflow Trigger
The system MUST trigger a Temporal workflow for every captured Slack message.

#### Scenario: Workflow started successfully
- **WHEN** a Slack message event is captured
- **THEN** a `SlackEchoWorkflow` is started with the message content and channel ID

### Requirement: Slack Message Echo
The `SlackEchoWorkflow` SHALL post the same message text back to the original Slack channel.

#### Scenario: Message echoed to Slack
- **WHEN** the `SlackEchoWorkflow` executes
- **THEN** it calls an activity to post the message text back to the Slack channel

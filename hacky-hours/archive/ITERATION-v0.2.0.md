# Iteration — Post v0.1.0

## Raw Capture

### 1. Web access / content pulling
- The tool cannot access websites or pull content from URLs
- The LLM API key alone doesn't enable web browsing — this is a tool/capability gap, not an API key config issue
- Users need the CEO to be able to read web pages (competitor research, articles, docs, etc.) as context for strategic advice
- This is a capability the wrapper layer needs to provide, not something the LLM can do on its own

### 2. Slack integration
- Want a bot on the Empathetech community Slack
- Use case: interact with the CEO through Slack, not just the CLI
- Minimum viable version: CLI drafts a message, sends it to a Slack channel via webhook
- Could be as simple as a `exec-in-a-box send-slack` command that takes the last CEO response or a custom message and posts it to a configured webhook
- Bigger version: a Slack bot that accepts questions and responds with board sessions

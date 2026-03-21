# Security Policy

## Reporting a Vulnerability

If you find a security issue in Executive in a Box, **please do not open a
public GitHub issue.** Security issues need to be handled privately so they
can be fixed before being disclosed.

### How to report

Send an email to: **[SECURITY EMAIL — to be configured]**

Or use GitHub's private vulnerability reporting:
1. Go to the Security tab of this repository
2. Click "Report a vulnerability"
3. Fill in the details

### What to include

- What you found (the more specific, the better)
- Steps to reproduce it, if you can
- What you think the impact is
- Any suggested fix, if you have one

### What to expect

- **Acknowledgment within 72 hours** — we'll confirm we received your report
  and are looking into it
- **A timeline within one week** — we'll tell you when we expect to have a
  fix or a decision
- **Credit** — if you want to be credited for the find, we'll include your
  name (or handle) in the fix commit and release notes

### What counts as a security issue

- Secrets or credentials exposed in code or commit history
- Prompt injection vulnerabilities that bypass the wrapper layer guardrails
- Ways to exfiltrate data from local storage to an unintended destination
- Bugs that cause the tool to send context to an LLM provider the user
  didn't configure
- Autonomy level bypasses (tool acts without user approval when it shouldn't)
- Any way for LLM output to trigger actions that weren't validated by the
  wrapper layer

### What is NOT a security issue (but still worth reporting as a regular issue)

- The LLM giving bad advice (that's a product quality issue, not a security issue)
- Feature requests for additional security controls
- Bugs that don't involve data exposure or unauthorized actions

## A note on scope

This is an open source community project. There is no paid security team and
no SLA. But we take security seriously because the people using this tool are
trusting it with real strategic information about their organizations.

If you report something, we will treat it with the urgency it deserves.

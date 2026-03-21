# ADR: Web content fetching as a wrapper layer capability

**Date:** 2026-03-21
**Status:** Accepted

## Context

The CEO tool cannot access web content. Users need it to read web pages
(competitor research, articles, documentation) as context for strategic
advice. LLMs cannot browse the web on their own — the tool must fetch
content and inject it into the prompt.

## Decision

Add a URL fetcher to the wrapper layer that:
1. Accepts one or more URLs from the user
2. Fetches the page content over HTTPS
3. Strips HTML to readable plain text
4. Injects the content into the prompt as a clearly labeled data section
5. Applies the same secret scanner and structural separation rules as
   all other context

## Rationale

- Keeps the capability in our code (wrapper layer), not the LLM
- Reuses existing prompt injection defenses (structural separation)
- No new credentials or services required — just HTTP requests
- Content is fetched on-demand, not stored (unless the user saves it)

## Tradeoffs

- Some sites block automated requests or require JavaScript rendering
  (we accept this limitation in MVP — plain HTTP fetch only)
- Fetched content could contain prompt injection attempts (mitigated
  by structural separation and output schema validation)
- Large pages need to be truncated to fit context windows

## Security considerations

- Fetched content is treated as untrusted data (same as user documents)
- Secret scanner runs on fetched content before injection
- URLs are logged in the session transcript so the user can verify
  what was included

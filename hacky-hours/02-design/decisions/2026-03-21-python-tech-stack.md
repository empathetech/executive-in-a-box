# ADR: Python as implementation language

**Date:** 2026-03-21
**Status:** Accepted

## Context

Executive in a Box needs a language that balances:
- Installation simplicity for non-technical users
- Contributor accessibility (low barrier to entry)
- LLM SDK support (Anthropic and OpenAI as first-class)

## Decision

Python, distributed as a pip-installable package (`executive-in-a-box`).
CLI entry point: `exec-in-a-box`.

## Rationale

- Most accessible language for new contributors
- First-class Anthropic and OpenAI SDKs
- `pip install` is a reasonable install experience
- Large ecosystem for future needs (MCP, Ollama bindings, etc.)

## Tradeoffs

- Requires Python runtime installed (unlike a Go binary)
- Slower than compiled languages (not a concern for a CLI advisory tool)
- Packaging/distribution is more complex than a single binary

## Alternatives considered

- **Node.js/TypeScript**: good SDK support, but npm ecosystem adds complexity
- **Go**: best install experience (single binary), but smaller contributor
  pool and less mature LLM SDKs

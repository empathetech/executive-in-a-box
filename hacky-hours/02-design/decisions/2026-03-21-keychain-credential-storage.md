# ADR: OS keychain for API key storage

**Date:** 2026-03-21
**Status:** Accepted

## Context

The original design stored API keys in `board/config.md` with
restricted file permissions (chmod 600). While this is a common
approach for CLI tools (e.g., `~/.aws/credentials`), plaintext
storage is a meaningful risk for our user base — people who may
not be familiar with file permission models and who may
inadvertently expose credentials.

## Decision

Store API keys in the operating system's keychain using the
`keyring` Python library:
- macOS: Keychain Access
- Windows: Credential Locker
- Linux: Secret Service (GNOME Keyring / KDE Wallet)

Environment variables (`EXEC_ANTHROPIC_API_KEY`,
`EXEC_OPENAI_API_KEY`) are supported as a fallback for headless
environments.

## Rationale

- Keys are encrypted at rest by the OS, not stored in plaintext
- Only accessible to the user's OS account
- Eliminates the risk of accidentally committing a key to git
- Familiar to users (same system as browser passwords)
- The `keyring` library is MIT-licensed and well-maintained

## Tradeoffs

- Adds a dependency (`keyring`)
- On some Linux systems without a desktop environment, the
  keychain backend may not be available (env vars are the
  fallback)
- Slightly more complex implementation than file-based storage
- Users can't easily inspect the stored key without using the
  OS keychain UI (this is a feature, not a bug)

## Impact

- `board/config.md` no longer contains the `api_key` field
- Config file no longer needs restricted permissions
- All code paths that read API keys go through the
  `credentials` module
- SECURITY_PRIVACY.md, ARCHITECTURE.md, SETUP_GUIDE.md, and
  PROVIDER_GUIDE.md updated to reflect this change

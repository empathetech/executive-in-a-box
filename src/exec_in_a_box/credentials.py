"""Secure credential storage using the OS keychain.

API keys are stored in the operating system's credential manager:
- macOS: Keychain
- Windows: Credential Locker
- Linux: Secret Service (GNOME Keyring, KDE Wallet)

Keys are encrypted at rest by the OS and only accessible to the
current user account. They are never stored in plaintext files.

Fallback: environment variables (EXEC_ANTHROPIC_API_KEY,
EXEC_OPENAI_API_KEY) are checked first, so users who prefer that
approach can use it instead.
"""

from __future__ import annotations

import os

import keyring

SERVICE_NAME = "executive-in-a-box"

# Maps provider name to keyring username and env var name
_PROVIDER_MAP = {
    "anthropic": {
        "keyring_user": "anthropic-api-key",
        "env_var": "EXEC_ANTHROPIC_API_KEY",
    },
    "openai": {
        "keyring_user": "openai-api-key",
        "env_var": "EXEC_OPENAI_API_KEY",
    },
}


def get_api_key(provider_name: str) -> str | None:
    """Retrieve an API key for the given provider.

    Checks in order:
    1. Environment variable (EXEC_ANTHROPIC_API_KEY or EXEC_OPENAI_API_KEY)
    2. OS keychain via keyring

    Returns None if not found in either location.
    """
    info = _PROVIDER_MAP.get(provider_name)
    if info is None:
        return None

    # Check env var first
    env_val = os.environ.get(info["env_var"])
    if env_val:
        return env_val

    # Check OS keychain
    try:
        return keyring.get_password(SERVICE_NAME, info["keyring_user"])
    except keyring.errors.KeyringError:
        return None


def store_api_key(provider_name: str, api_key: str) -> None:
    """Store an API key in the OS keychain."""
    info = _PROVIDER_MAP.get(provider_name)
    if info is None:
        raise ValueError(f"Unknown provider: {provider_name}")

    keyring.set_password(SERVICE_NAME, info["keyring_user"], api_key)


def delete_api_key(provider_name: str) -> None:
    """Remove an API key from the OS keychain."""
    info = _PROVIDER_MAP.get(provider_name)
    if info is None:
        return

    try:
        keyring.delete_password(SERVICE_NAME, info["keyring_user"])
    except keyring.errors.PasswordDeleteError:
        pass  # Key didn't exist — that's fine

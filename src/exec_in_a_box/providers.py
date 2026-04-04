"""LLM provider adapter layer.

Abstracts the connection to LLM APIs so the board engine doesn't care which
model is powering which archetype.

Reference: hacky-hours/02-design/ARCHITECTURE.md § LLM Provider Adapter
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    """Structured response from an LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int


class ProviderError(Exception):
    """Base error for provider failures. Contains a user-friendly message."""

    def __init__(self, user_message: str, debug_message: str | None = None):
        self.user_message = user_message
        self.debug_message = debug_message or user_message
        super().__init__(self.user_message)


class Provider(ABC):
    """Base interface for LLM providers."""

    name: str

    @abstractmethod
    def send(self, system_prompt: str, user_message: str) -> ProviderResponse:
        """Send a prompt and return the response."""

    @abstractmethod
    def test_connection(self) -> bool:
        """Test that the API key is valid. Returns True on success, raises ProviderError on failure."""


class AnthropicProvider(Provider):
    """Adapter for the Anthropic (Claude) API."""

    name = "anthropic"

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-6"):
        self.api_key = api_key or os.environ.get("EXEC_ANTHROPIC_API_KEY")
        self.model = model
        if not self.api_key:
            raise ProviderError(
                "No Anthropic API key found. Set EXEC_ANTHROPIC_API_KEY or "
                "provide it during setup."
            )

    def _client(self):
        import anthropic

        return anthropic.Anthropic(api_key=self.api_key)

    def send(self, system_prompt: str, user_message: str) -> ProviderResponse:
        import anthropic

        try:
            client = self._client()
            message = client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return ProviderResponse(
                content=message.content[0].text,
                model=message.model,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
        except anthropic.AuthenticationError:
            raise ProviderError(
                "Your Anthropic API key was rejected. Check that it's correct "
                "and that your account has billing set up."
            )
        except anthropic.RateLimitError:
            raise ProviderError(
                "Anthropic rate limit reached. Wait a minute and try again."
            )
        except anthropic.APIConnectionError:
            raise ProviderError(
                "Couldn't reach the Anthropic API. Check your internet connection."
            )
        except anthropic.APIError as e:
            raise ProviderError(
                "Something went wrong with the Anthropic API. Try again in a moment.",
                debug_message=str(e),
            )

    def test_connection(self) -> bool:
        import anthropic

        try:
            client = self._client()
            client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'ok'."}],
            )
            return True
        except anthropic.AuthenticationError:
            raise ProviderError(
                "Your Anthropic API key was rejected. Check that it's correct "
                "and that your account has billing set up."
            )
        except anthropic.APIConnectionError:
            raise ProviderError(
                "Couldn't reach the Anthropic API. Check your internet connection."
            )
        except anthropic.APIError as e:
            raise ProviderError(
                "Something went wrong while testing the connection.",
                debug_message=str(e),
            )


class OpenAIProvider(Provider):
    """Adapter for the OpenAI (GPT) API."""

    name = "openai"

    def __init__(self, api_key: str | None = None, model: str = "gpt-4.1"):
        self.api_key = api_key or os.environ.get("EXEC_OPENAI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ProviderError(
                "No OpenAI API key found. Set EXEC_OPENAI_API_KEY or "
                "provide it during setup."
            )

    def _client(self):
        from openai import OpenAI

        return OpenAI(api_key=self.api_key)

    def send(self, system_prompt: str, user_message: str) -> ProviderResponse:
        from openai import (
            APIConnectionError,
            APIError,
            AuthenticationError,
            RateLimitError,
        )

        try:
            client = self._client()
            response = client.chat.completions.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            choice = response.choices[0]
            return ProviderResponse(
                content=choice.message.content,
                model=response.model,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            )
        except AuthenticationError:
            raise ProviderError(
                "Your OpenAI API key was rejected. Check that it's correct "
                "and that your account has billing set up."
            )
        except RateLimitError:
            raise ProviderError(
                "OpenAI rate limit reached. Wait a minute and try again."
            )
        except APIConnectionError:
            raise ProviderError(
                "Couldn't reach the OpenAI API. Check your internet connection."
            )
        except APIError as e:
            raise ProviderError(
                "Something went wrong with the OpenAI API. Try again in a moment.",
                debug_message=str(e),
            )

    def test_connection(self) -> bool:
        from openai import APIConnectionError, APIError, AuthenticationError

        try:
            client = self._client()
            client.chat.completions.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say 'ok'."}],
            )
            return True
        except AuthenticationError:
            raise ProviderError(
                "Your OpenAI API key was rejected. Check that it's correct "
                "and that your account has billing set up."
            )
        except APIConnectionError:
            raise ProviderError(
                "Couldn't reach the OpenAI API. Check your internet connection."
            )
        except APIError as e:
            raise ProviderError(
                "Something went wrong while testing the connection.",
                debug_message=str(e),
            )


class OllamaProvider(Provider):
    """Adapter for Ollama (local LLM server).

    Ollama must be running locally. Default base URL: http://localhost:11434.
    API key is not required — Ollama is fully local.

    Reference: hacky-hours/02-design/ARCHITECTURE.md § LLM Provider Adapter
    """

    name = "ollama"

    def __init__(
        self,
        api_key: str | None = None,  # accepted but ignored (no auth for Ollama)
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def send(self, system_prompt: str, user_message: str) -> ProviderResponse:
        import httpx

        try:
            resp = httpx.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "stream": False,
                },
                timeout=120.0,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"]
            # Ollama doesn't expose token counts in the same way — use estimates
            return ProviderResponse(
                content=content,
                model=self.model,
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
            )
        except httpx.ConnectError:
            raise ProviderError(
                "Couldn't connect to Ollama. Make sure it's running: ollama serve"
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"Ollama returned an error: {e.response.status_code}",
                debug_message=str(e),
            )
        except (KeyError, ValueError) as e:
            raise ProviderError(
                "Unexpected response format from Ollama.",
                debug_message=str(e),
            )

    def test_connection(self) -> bool:
        import httpx

        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            resp.raise_for_status()
            return True
        except httpx.ConnectError:
            raise ProviderError(
                "Couldn't connect to Ollama. Make sure it's running: ollama serve"
            )
        except httpx.HTTPError as e:
            raise ProviderError(
                "Ollama server responded with an error.",
                debug_message=str(e),
            )


# Registry of available providers
PROVIDERS: dict[str, type[Provider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
}


def create_provider(
    provider_name: str, api_key: str | None = None, model: str | None = None
) -> Provider:
    """Create a provider instance by name.

    Raises ProviderError if the provider is not recognized.
    """
    cls = PROVIDERS.get(provider_name)
    if cls is None:
        raise ProviderError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {', '.join(PROVIDERS.keys())}"
        )
    kwargs: dict = {}
    if api_key is not None:
        kwargs["api_key"] = api_key
    if model is not None:
        kwargs["model"] = model
    return cls(**kwargs)

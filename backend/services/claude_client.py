import anthropic
import os
from typing import Optional


class ClaudeClient:
    """
    Wrapper around the Anthropic Python SDK.
    Handles model selection, system prompts, and response parsing.
    """

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set in environment.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def complete(
        self,
        user_message: str,
        system_prompt: str,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a single-turn message to Claude and return the text response.

        Args:
            user_message: The user turn content.
            system_prompt: The system-level instruction for Claude.
            temperature: 0.0-1.0. Lower = more deterministic (use for scoring).
                         Higher = more creative (use for cover letters).
            max_tokens: Override default token limit.

        Returns:
            The assistant's response as a plain string.
        """
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=max_tokens or self.MAX_TOKENS,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        # Extract text from the first content block
        return response.content[0].text

    def complete_with_history(
        self,
        messages: list[dict],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """
        Send a multi-turn conversation to Claude.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
            system_prompt: System instruction.
            temperature: Sampling temperature.

        Returns:
            The assistant's latest response as a plain string.
        """
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
        )
        return response.content[0].text


# Module-level singleton — lazily initialized on first use
# This allows importing the module in tests without a real API key
_claude_instance: ClaudeClient | None = None


def get_claude() -> ClaudeClient:
    global _claude_instance
    if _claude_instance is None:
        _claude_instance = ClaudeClient()
    return _claude_instance


# Convenience alias — services import this
class _LazyClient:
    """Proxy that defers ClaudeClient instantiation until first API call."""
    def __getattr__(self, name):
        return getattr(get_claude(), name)


claude = _LazyClient()

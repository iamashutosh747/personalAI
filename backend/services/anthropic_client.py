from anthropic import Anthropic

from backend.config import settings

_client = Anthropic(api_key=settings.anthropic_api_key)


def _complete(model: str, messages: list[dict], max_tokens: int = 1024, system: str | None = None) -> str:
    kwargs: dict = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system
    response = _client.messages.create(**kwargs)
    # Only concatenate text blocks; skip thinking/other block types.
    return "".join(block.text for block in response.content if block.type == "text")


def ask_claude(messages: list[dict], system: str | None = None) -> str:
    """Send a message history to the main reasoning model and return its text reply.

    `messages` is a list of {"role": "user"|"assistant", "content": str} dicts,
    oldest first.
    """
    return _complete(settings.claude_model_main, messages, system=system)


def ask_utility(messages: list[dict], max_tokens: int = 512) -> str:
    """Same as ask_claude, but uses the cheap utility model for background tasks."""
    return _complete(settings.claude_model_utility, messages, max_tokens=max_tokens)

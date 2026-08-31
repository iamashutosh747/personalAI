from anthropic import Anthropic

from backend.config import settings

_client = Anthropic(api_key=settings.anthropic_api_key)


def ask_claude(messages: list[dict]) -> str:
    """Send a message history to Claude and return its text reply.

    `messages` is a list of {"role": "user"|"assistant", "content": str} dicts,
    oldest first.
    """
    response = _client.messages.create(
        model=settings.claude_model_main,
        max_tokens=1024,
        messages=messages,
    )
    # Only concatenate text blocks; skip thinking/other block types.
    return "".join(block.text for block in response.content if block.type == "text")

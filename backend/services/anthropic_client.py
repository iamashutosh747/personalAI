from anthropic import Anthropic

from backend.config import settings

_client = Anthropic(api_key=settings.anthropic_api_key)


def ask_claude(message: str) -> str:
    """Send a single message to Claude and return its text reply."""
    response = _client.messages.create(
        model=settings.claude_model_main,
        max_tokens=1024,
        messages=[{"role": "user", "content": message}],
    )
    # Only concatenate text blocks; skip thinking/other block types.
    return "".join(block.text for block in response.content if block.type == "text")

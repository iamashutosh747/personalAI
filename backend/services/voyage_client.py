import voyageai

from backend.config import settings

_client = voyageai.Client(api_key=settings.voyage_api_key)


def embed_text(text: str, input_type: str) -> list[float]:
    """Embed one piece of text.

    `input_type` must be "document" when storing a memory, or "query" when
    searching — Voyage tunes the embedding differently for each.
    """
    result = _client.embed(
        [text],
        model=settings.voyage_model,
        input_type=input_type,
        output_dimension=settings.voyage_embedding_dimension,
    )
    return result.embeddings[0]

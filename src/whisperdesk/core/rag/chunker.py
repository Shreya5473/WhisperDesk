def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits text into chunks of roughly chunk_size characters, with
    `overlap` characters repeated between consecutive chunks.
    """
    text = text.strip()
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    min_chunk_fraction = 0.5  # boundary must be at least halfway through the window to count

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            search_from = start + int(chunk_size * min_chunk_fraction)
            boundary = text.rfind(". ", search_from, end)
            if boundary == -1:
                boundary = text.rfind("\n", search_from, end)
            if boundary != -1:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = end - overlap
        if next_start <= start:
            next_start = end  # no overlap rather than risk zero/negative progress
        start = next_start

    return chunks
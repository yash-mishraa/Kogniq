def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a string.

    This is a rough heuristic (approx 1.3 to 1.5 tokens per word)
    intended as a fast fallback when a concrete tokenizer is not available.

    Args:
        text: The string to estimate.

    Returns:
        An integer representing the estimated token count.
    """
    if not text:
        return 0
    words = len(text.split())
    # A common rule of thumb is 1 token ~= 4 chars in English or ~1.3 tokens per word
    return int(words * 1.3)

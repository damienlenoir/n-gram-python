"""Character n-gram extraction and comparison.

An n-gram is a subsequence of n elements. Here, the elements are
characters (letters + spaces), not words.

Example with n=3 and the text "chat":
    "cha", "hat"

Why characters instead of words for language detection?
- It works even when the word is unknown ("antidisestablishmentarianism").
- Languages already differ by letter patterns
  (French: "es", "de", "tion" / English: "th", "ing").
- Short text is often enough.
"""

from __future__ import annotations

import math
import re
from collections import Counter

# Multiple consecutive spaces become a single space.
_WHITESPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Prepare text before splitting into n-grams.

    - lowercase: "Paris" and "paris" must count the same
    - keep letters (including accents: é, ñ, ß…) and spaces
    - remove punctuation and digits, not useful for language detection
    """
    characters: list[str] = []
    for character in text.lower():
        if character.isspace():
            characters.append(" ")
        elif character.isalpha():
            characters.append(character)
    return _WHITESPACE.sub(" ", "".join(characters)).strip()


def extract_ngrams(text: str, n: int) -> list[str]:
    """Split text with a sliding window of size n.

    For "for example" and n=2, we get among others "fo", "or", "r ",
    " e", "ex", … (the space is part of n-grams: it marks word
    boundaries, which helps recognize a language).
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    cleaned = normalize(text)
    if not cleaned:
        return []
    if len(cleaned) <= n:
        return [cleaned]

    # Sliding window: at each position i, take n characters.
    return [cleaned[i : i + n] for i in range(len(cleaned) - n + 1)]


def count_ngrams(text: str, n: int) -> Counter[str]:
    """Count how many times each n-gram appears."""
    return Counter(extract_ngrams(text, n))


def ngram_frequencies(text: str, n: int) -> dict[str, float]:
    """Convert counts to relative frequencies (sum = 1.0).

    Example: if "es" appears 10 times out of 100 n-grams, its frequency
    is 0.10. This lets us compare texts of different lengths.
    """
    counts = count_ngrams(text, n)
    total = sum(counts.values())
    if total == 0:
        return {}
    return {gram: count / total for gram, count in counts.items()}


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    """Measure how similar two n-gram profiles are.

    Each profile is a vector: one dimension per n-gram, the value
    is the frequency. Cosine similarity is:
        1.0  → same direction (identical profiles)
        0.0  → nothing in common

    Formula:  (A · B) / (|A| × |B|)
    """
    if not a or not b:
        return 0.0

    # Dot product: only multiply n-grams present on both sides.
    common_keys = set(a) & set(b)
    dot_product = sum(a[key] * b[key] for key in common_keys)

    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)

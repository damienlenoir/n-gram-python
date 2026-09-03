"""Tests for the algorithm core: extraction and similarity."""

from app.ngrams import cosine_similarity, extract_ngrams, normalize, ngram_frequencies


def test_normalize_lowercase_and_punctuation() -> None:
    assert normalize("  Paris, 2024 ! ") == "paris"


def test_extract_trigrams() -> None:
    # "chat" → cha, hat
    assert extract_ngrams("chat", n=3) == ["cha", "hat"]


def test_extract_bigrams_with_space() -> None:
    grams = extract_ngrams("le chat", n=2)
    assert "le" in grams
    assert "e " in grams
    assert " c" in grams
    assert "ch" in grams


def test_frequencies_sum_to_one() -> None:
    freqs = ngram_frequencies("banane", n=2)
    assert freqs
    assert abs(sum(freqs.values()) - 1.0) < 1e-9


def test_cosine_identical() -> None:
    profile = ngram_frequencies("bonjour tout le monde", n=3)
    assert cosine_similarity(profile, profile) == 1.0


def test_cosine_nothing_in_common() -> None:
    a = {"aa": 1.0}
    b = {"zz": 1.0}
    assert cosine_similarity(a, b) == 0.0

"""Language detection: compare text against learned profiles.

General idea (classic approach, close to Cavnar & Trenkle, 1994):

1. For each language, we have a small corpus (.txt file).
2. We extract a *profile* from it: n-gram frequencies.
3. For unknown text, we compute the same profile.
4. We compare it to each language (cosine similarity).
5. The closest language wins.

Profiles depend on n: unigrams (n=1) = simple letter frequencies;
trigrams (n=3) = sequences, often more discriminative.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.ngrams import count_ngrams, cosine_similarity, ngram_frequencies

# Display names in the UI and API responses. The key is the filename without .txt.
LANGUAGE_NAMES: dict[str, str] = {
    "fr": "French",
    "en": "English",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
}


@dataclass
class LanguageScoreData:
    code: str
    name: str
    similarity: float
    probability: float


@dataclass
class ObservedNGram:
    gram: str
    count: int
    frequency: float


@dataclass
class DetectionResult:
    language: str
    language_name: str
    n: int
    scores: list[LanguageScoreData]
    top_ngrams: list[ObservedNGram]


class LanguageDetector:
    """Load corpora at startup, then classify texts."""

    def __init__(self, corpus: dict[str, str]) -> None:
        if not corpus:
            raise ValueError("No language corpus provided.")
        self.corpus = corpus
        # Cache: don't recompute a language profile on every request.
        self._profile_cache: dict[int, dict[str, dict[str, float]]] = {}

    @classmethod
    def from_directory(cls, directory: Path) -> LanguageDetector:
        """Read all .txt files in a directory (fr.txt → language "fr")."""
        corpus: dict[str, str] = {}
        for path in sorted(directory.glob("*.txt")):
            corpus[path.stem] = path.read_text(encoding="utf-8")
        return cls(corpus)

    def languages(self) -> list[dict[str, str]]:
        return [
            {"code": code, "name": LANGUAGE_NAMES.get(code, code)}
            for code in sorted(self.corpus)
        ]

    def _profiles(self, n: int) -> dict[str, dict[str, float]]:
        if n not in self._profile_cache:
            self._profile_cache[n] = {
                code: ngram_frequencies(text, n)
                for code, text in self.corpus.items()
            }
        return self._profile_cache[n]

    def detect(self, text: str, n: int = 3, top_k: int = 12) -> DetectionResult:
        text_profile = ngram_frequencies(text, n)
        if not text_profile:
            raise ValueError(
                "The text contains no letters. "
                "Add some words so n-grams can be extracted."
            )

        raw_scores: list[tuple[str, float]] = []
        for code, language_profile in self._profiles(n).items():
            similarity = cosine_similarity(text_profile, language_profile)
            raw_scores.append((code, similarity))

        raw_scores.sort(key=lambda item: item[1], reverse=True)
        total = sum(max(sim, 0.0) for _, sim in raw_scores)

        scores = [
            LanguageScoreData(
                code=code,
                name=LANGUAGE_NAMES.get(code, code),
                similarity=round(similarity, 4),
                # Not a true statistical probability: we normalize
                # similarities so they sum to 1 (more readable).
                probability=round((max(similarity, 0.0) / total) if total else 0.0, 4),
            )
            for code, similarity in raw_scores
        ]

        counts = count_ngrams(text, n)
        total_ngrams = sum(counts.values())
        top_ngrams = [
            ObservedNGram(
                gram=gram,
                count=count,
                frequency=round(count / total_ngrams, 4),
            )
            for gram, count in counts.most_common(top_k)
        ]

        winner = scores[0]
        return DetectionResult(
            language=winner.code,
            language_name=winner.name,
            n=n,
            scores=scores,
            top_ngrams=top_ngrams,
        )

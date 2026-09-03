"""Pydantic models: the JSON contract between the browser and FastAPI.

Pydantic validates data: an out-of-range `n` or empty text
automatically returns a 422 error, without manual if/else checks.
"""

from pydantic import BaseModel, ConfigDict, Field


class DetectRequest(BaseModel):
    """Input for language detection."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "The little cat drinks milk by the window.",
                    "n": 3,
                }
            ]
        }
    )

    text: str = Field(
        ...,
        min_length=1,
        max_length=10_000,
        description="Text to analyze (letters and spaces are kept).",
        examples=["The little cat drinks milk by the window."],
    )
    n: int = Field(
        default=3,
        ge=1,
        le=5,
        description="N-gram size: 1 = letters, 3 = trigrams (recommended).",
        examples=[3],
    )


class LanguageScore(BaseModel):
    """Similarity score for one supported language."""

    code: str = Field(description="ISO-style language code (e.g. fr, en).")
    name: str = Field(description="English display name of the language.")
    similarity: float = Field(description="Cosine similarity with the text profile (0–1).")
    probability: float = Field(
        description="Normalized similarity share across languages (sums to 1)."
    )


class NGramInfo(BaseModel):
    """One of the most frequent n-grams in the submitted text."""

    gram: str = Field(description="N-gram string (spaces appear as literal spaces).")
    count: int = Field(description="Number of occurrences in the text.")
    frequency: float = Field(description="Relative frequency among all n-grams.")


class DetectResponse(BaseModel):
    """Language detection result with ranking and top n-grams."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "language": "en",
                    "language_name": "English",
                    "n": 3,
                    "scores": [
                        {
                            "code": "en",
                            "name": "English",
                            "similarity": 0.92,
                            "probability": 0.65,
                        }
                    ],
                    "top_ngrams": [
                        {"gram": "the", "count": 4, "frequency": 0.08},
                    ],
                }
            ]
        }
    )

    language: str = Field(description="Winning language code.")
    language_name: str = Field(description="English name of the winning language.")
    n: int = Field(description="N-gram size used for detection.")
    scores: list[LanguageScore] = Field(description="All languages ranked by similarity.")
    top_ngrams: list[NGramInfo] = Field(
        description="Most frequent n-grams extracted from the input text."
    )


class LanguageInfo(BaseModel):
    """A language supported by the detector."""

    code: str = Field(description="Language code matching the sample file name.")
    name: str = Field(description="English display name.")

"""The detector should recognize fairly typical texts."""

from app.detector import LanguageDetector
from app.main import detector


def test_languages_loaded() -> None:
    codes = {item["code"] for item in detector.languages()}
    assert codes == {"de", "en", "es", "fr", "it", "pt"}


def test_detects_french() -> None:
    text = (
        "Les enfants jouent dans la cour pendant que les oiseaux "
        "chantent près des fenêtres de la maison."
    )
    result = detector.detect(text, n=3)
    assert result.language == "fr"


def test_detects_english() -> None:
    text = (
        "The children are playing in the yard while the birds "
        "sing near the windows of the house."
    )
    result = detector.detect(text, n=3)
    assert result.language == "en"


def test_detects_german() -> None:
    text = (
        "Die Kinder spielen im Hof, während die Vögel in der Nähe "
        "der Fenster des Hauses singen."
    )
    result = detector.detect(text, n=3)
    assert result.language == "de"


def test_detects_portuguese() -> None:
    text = (
        "Não consigo encontrar a informação sobre a transação. "
        "A solução está na documentação da aplicação."
    )
    result = detector.detect(text, n=3)
    assert result.language == "pt"


def test_empty_corpus_rejected() -> None:
    try:
        LanguageDetector({})
    except ValueError:
        return
    raise AssertionError("An empty corpus should raise ValueError")

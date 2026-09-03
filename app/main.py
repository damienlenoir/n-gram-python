"""FastAPI app: bridge between the web page and the Python detector.

Run from the project root:

    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

Then open http://127.0.0.1:8000
Interactive docs (very useful for learning): http://127.0.0.1:8000/docs
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.detector import LanguageDetector
from app.schemas import DetectRequest, DetectResponse, LanguageInfo, LanguageScore, NGramInfo

ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = ROOT / "data" / "samples"
STATIC_DIR = ROOT / "static"

detector = LanguageDetector.from_directory(SAMPLES_DIR)

app = FastAPI(
    title="N-gram Language Detector",
    description=(
        "Detects the language of a text by comparing its character "
        "n-grams to language profiles learned from small corpora."
    ),
    version="0.1.0",
    docs_url=None,
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "detection",
            "description": "Language detection and supported languages.",
        },
    ],
)


@app.get("/docs", include_in_schema=False)
def swagger_docs() -> HTMLResponse:
    """Swagger UI in English (avoids French UI from browser locale)."""
    response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API docs",
        swagger_ui_parameters={"tryItOutEnabled": True},
    )
    response.body = response.body.replace(b"<html>", b'<html lang="en">')
    return response


@app.get(
    "/api/languages",
    response_model=list[LanguageInfo],
    tags=["detection"],
    summary="List supported languages",
)
def list_languages() -> list[LanguageInfo]:
    """Return every language that has a training sample in `data/samples/`."""
    return [LanguageInfo(**item) for item in detector.languages()]


@app.post(
    "/api/detect",
    response_model=DetectResponse,
    tags=["detection"],
    summary="Detect language",
    responses={
        400: {"description": "Text contains no letters after normalization."},
        422: {"description": "Invalid request body (empty text, n out of range, etc.)."},
    },
)
def detect(request: DetectRequest) -> DetectResponse:
    """Compare the text profile to each language and return the ranking."""
    try:
        result = detector.detect(request.text, n=request.n)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return DetectResponse(
        language=result.language,
        language_name=result.language_name,
        n=result.n,
        scores=[
            LanguageScore(
                code=score.code,
                name=score.name,
                similarity=score.similarity,
                probability=score.probability,
            )
            for score in result.scores
        ],
        top_ngrams=[
            NGramInfo(
                gram=item.gram,
                count=item.count,
                frequency=item.frequency,
            )
            for item in result.top_ngrams
        ],
    )


@app.get("/", include_in_schema=False)
def home_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# /static/styles.css and /static/app.js
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

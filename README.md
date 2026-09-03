# N-gram Language Detector

A small project for learning **Python**, its ecosystem, and **FastAPI**.
The goal: guess the language of a text by comparing **character n-grams**.

The idea comes from the Wikipedia article
[N-gram](https://en.wikipedia.org/wiki/N-gram): a subsequence of
`n` elements extracted from a sequence. Here, the elements are letters
(and spaces), not words.

## How it works

1. **Normalize** the text (lowercase, keep letters and spaces).
2. Slide a window of size `n`: for `chat` and `n=3` → `cha`, `hat`.
3. Count occurrences, then convert to **frequencies** (to compare texts of different lengths).
4. Each language has a **profile** computed from a small corpus (`data/samples/fr.txt`, etc.).
5. Compare the text profile to each language using **cosine similarity**.
6. The closest language wins.

`n=1` = letter frequencies. `n=3` (trigrams) is often the best
trade-off. Very short text makes ranking unstable — that's expected.

## Running the project (Windows)

In PowerShell, from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then open:

- the UI: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- the auto-generated FastAPI docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Tests:

```powershell
python -m pytest -q
```

## Structure

```
n-gram-py/
├── app/
│   ├── ngrams.py      # extraction, frequencies, cosine similarity
│   ├── detector.py    # comparison against language profiles
│   ├── schemas.py     # JSON contract (Pydantic)
│   └── main.py        # FastAPI routes
├── data/samples/      # training corpus (one .txt per language)
├── static/            # vanilla HTML / CSS / JS page
└── tests/
```

## Ideas for next steps

Explore these in order — useful real-world Python:

- Read `app/ngrams.py`: `list`, `dict`, `Counter`, list comprehensions.
- Change `n` in the UI and observe the displayed n-grams.
- Add a language: a `data/samples/nl.txt` file is enough.
- Replace cosine similarity with L1 distance (`sum(abs(a-b))`).
- Smooth missing n-grams in the corpus (the zero-frequency problem, described on Wikipedia).
- Split `main.py`: detector injection, configuration, logging.
- Add a `Dockerfile`, or type more strictly with `mypy`.

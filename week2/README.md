# Action Item Extractor

A minimal **FastAPI** + **SQLite** application that takes free‑form notes
and turns them into a checklist of actionable items.  Notes can be
persisted, action items marked done, and you can even delegate the
extraction logic to a local LLM via [Ollama](https://ollama.com/).

The project ships with a very small vanilla‑HTML frontend
(`frontend/index.html`) that exercises the API, but all functionality is
available over HTTP.

---

## Getting started

### Requirements

- Python 3.10+  
- [Poetry](https://python-poetry.org/) (recommended) *or* `pip`
- [Ollama](https://ollama.com/) if you intend to use the LLM endpoint

### Install

```sh
git clone <repo-url>
cd week2                     # project root

# optional virtualenv
python -m venv .venv
# Unix/macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# install dependencies
poetry install

# alternatively using pip
# pip install fastapi uvicorn sqlalchemy pydantic requests python-dotenv ollama


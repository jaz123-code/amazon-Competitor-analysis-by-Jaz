# Amazon Competitor Analysis by Jaz

Lightweight Streamlit app to search Amazon for competitor product listings, scrape product details, store results locally, and optionally analyze competitors with an LLM (OpenAI via LangChain).

Important: this project uses external APIs (Oxylabs) and OpenAI — you must provide API credentials in environment variables before running.

## What it does
- Search Amazon for competitor products using Oxylabs Realtime scraping.
- Scrape product details (title, price, ratings, images, buybox, etc.).
- Store results in a local TinyDB database at `data/db.json`.
- Optional LLM-based analysis (requires `OPENAI_API_KEY`).

## Quick start

1. Create and activate a Python 3.12 virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies (this project uses `pyproject.toml` — adjust as needed):

```bash
pip install -r requirements.txt  # if you have one, or use your preferred method
```

3. Set environment variables (required):

- `OXYLABS_USERNAME` and `OXYLABS_PASSWORD` — your Oxylabs Realtime credentials
- `OPENAI_API_KEY` — required only if you want to run LLM analysis
- Optional: `OPENAI_MODEL` to select a model (defaults to `gpt-3.5-turbo`)

Example (macOS / zsh):

```bash
export OXYLABS_USERNAME="your_oxylabs_user"
export OXYLABS_PASSWORD="your_oxylabs_pass"
export OPENAI_API_KEY="sk-..."
```

4. Run the Streamlit app:

```bash
streamlit run main.py
```

## Files of interest
- `main.py` — Streamlit app entry
- `src/oxylabs_client.py` — Oxylabs request payloads and response normalization
- `src/services.py` — Orchestrates searches and scrapes, persists results to `data/db.json`
- `src/llm.py` — LLM analysis helper (LangChain/OpenAI)
- `src/db.py` — TinyDB wrapper

## Notes & privacy
- `data/db.json` is ignored by `.gitignore` to avoid committing scraped data or secrets.
- Do not commit API keys or personal tokens. Use environment variables or a secure secrets manager.

## Contributing
Feel free to open issues or PRs. For big changes (CI, Docker, logging to files), I can help add them.

## License
Add a license file if you plan to publish this publicly.


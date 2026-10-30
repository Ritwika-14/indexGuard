# IndexGuard — Phase 2
A learning project for Python backend engineering and financial data quality.

## Requirements
- Python 3.13
- Docker Desktop for local PostgreSQL

## Windows / PowerShell
1. Copy `.env.example` to `.env`.
2. Create and activate a virtual environment if needed:
   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -e ".[dev]"
   ```
4. Start PostgreSQL (Docker Desktop must be running):
   ```powershell
   docker compose up -d db
   docker compose ps
   ```
5. Create the tables:
   ```powershell
   python -m app.init_db
   ```
6. Start the API:
   ```powershell
   python -m uvicorn app.main:app --reload
   ```

## Verify
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/health/db
- http://127.0.0.1:8000/docs

Expected database health response: `{"status":"ok","database":"connected"}`.

## Phase 2 model
`ingestion_batches` stores batch metadata and counts.
`index_constituents` stores simulated company data and references its batch.
Database constraints prevent duplicate tickers within a batch, non-positive prices,
negative market caps, and weights outside 0–1. Batch-level weight totals are a Phase 3 rule.

The local credentials in `compose.yaml` are for development only. Never commit `.env`
or use these credentials in a public deployment. `create_all` is for local learning;
production migrations will be added later.

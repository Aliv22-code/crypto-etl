# Crypto ETL Pipeline

A production-grade data engineering pipeline that fetches live crypto prices from CoinGecko, transforms them with dbt, and stores them in a cloud Postgres database — running automatically every 6 hours.

---

## Architecture

```
CoinGecko API (free)
      │ every 6 hours
      ▼
Python ETL
  ├── extract.py   → fetch prices
  ├── validate.py  → data quality checks
  └── load.py      → save to Postgres
      │
      ▼
Supabase (cloud Postgres)
  └── public.crypto_prices
      │
      ▼
dbt transformations
  ├── analytics.stg_crypto_prices
  ├── analytics.daily_coin_summary
  └── analytics.top_movers
      │
      ▼
Prefect Cloud (scheduling + monitoring)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.11 |
| Extraction | requests |
| Loading | psycopg2 |
| Transformation | dbt Core |
| Orchestration | Prefect Cloud |
| Database | Supabase (Postgres) |
| Containerisation | Docker |
| CI/CD | GitHub Actions |
| Deployment | Railway |
| Testing | pytest, dbt tests |
| Linting | ruff |

---

## Features

- Fetches live prices for 5 coins every 6 hours — Bitcoin, Ethereum, Solana, Cardano, Dogecoin
- Data quality validation before loading — drops bad records automatically
- 3 dbt models — staging view + 2 analytics tables
- 14 automated data quality tests (built-in + custom SQL)
- 11 pytest tests — unit + integration
- Full CI/CD — linting, tests, coverage gate, dbt, Docker build on every push
- Auto deploys to Railway on every push to main
- Monitored via Prefect Cloud dashboard with retry on failure

---

## Project Structure

```
crypto-pipeline/
├── pipelines/
│   ├── extract.py        fetch from CoinGecko API
│   ├── validate.py       data quality checks
│   ├── load.py           save to Postgres
│   ├── pipeline.py       orchestrate ETL steps
│   └── flow.py           Prefect flow + schedule
├── dbt_project/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── sources.yml
│       │   ├── schema.yml
│       │   └── stg_crypto_prices.sql
│       └── marts/
│           ├── daily_coin_summary.sql
│           └── top_movers.sql
│   └── tests/
│       ├── assert_positive_prices.sql
│       └── assert_all_coins_present.sql
├── tests/
│   ├── test_extract.py
│   ├── test_load.py
│   ├── test_pipeline.py
│   └── test_flow.py
├── sql/
│   └── init.sql
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── render.yaml
├── .coveragerc
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml
```

---

## Data Models

### Raw layer — `public` schema
| Table | Description |
|---|---|
| `crypto_prices` | Raw price records from CoinGecko |

### Analytics layer — `analytics` schema
| Model | Type | Description |
|---|---|---|
| `stg_crypto_prices` | view | Clean view with derived time fields |
| `daily_coin_summary` | table | Avg / high / low price per coin per day |
| `top_movers` | table | Latest snapshot with gainer / loser / stable label |

---

## CI/CD Pipeline

Every push to `main` automatically runs:

```
1. ruff lint
2. pytest unit tests
3. pytest integration tests (local Postgres)
4. coverage check — 70% minimum
5. pipeline.py run
6. dbt run + dbt test
7. docker build
8. Railway auto deploy
```

---

## Local Setup

```bash
# 1. clone repo
git clone https://github.com/Aliv22-code/crypto-etl
cd crypto-etl

# 2. create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. install dependencies
pip install -r requirements.txt

# 4. copy env file and fill in values
cp .env.example .env

# 5. start local Postgres
docker-compose up -d

# 6. run pipeline
python pipelines/pipeline.py

# 7. run dbt
cd dbt_project
dbt run --profiles-dir .
dbt test --profiles-dir .

# 8. run tests
cd ..
pytest -v
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Local Docker
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crypto_db
DB_USER=crypto_user
DB_PASSWORD=crypto_pass

# Supabase (production)
# DB_HOST=aws-0-xx.pooler.supabase.com
# DB_PORT=6543
# DB_NAME=postgres
# DB_USER=postgres.xxxxxxxxxxxx
# DB_PASSWORD=your-supabase-password

# Prefect Cloud
PREFECT_API_KEY=your-prefect-api-key
PREFECT_API_URL=https://api.prefect.cloud/api/accounts/<id>/workspaces/<id>
```

---

## Running Tests

```bash
# all tests
pytest -v

# unit tests only (no DB needed)
pytest tests/test_extract.py tests/test_validate.py -v

# integration tests (requires Docker Postgres)
pytest tests/test_load.py -v

# with coverage
pytest --cov=pipelines --cov-report=term-missing
```

---

## Deployment

Pipeline runs on **Railway** as a Docker background worker.
Database hosted on **Supabase** free tier.
Orchestrated by **Prefect Cloud** free tier.

Every push to `main` → Railway auto-redeploys the container.

---

## What's Next

- Convert Prefect flow to Airflow DAG
- Build a Streamlit dashboard on top of Supabase data
- Add more data sources — stock prices, fear & greed index
- Publish dbt docs as a website
- Add Slack alerts on pipeline failure
# 100x Data Engineer Assessment

## Repository Overview

This workspace hosts my solution for the 100x Home at-home data engineering assessment. The upstream skeleton repository and dataset are mirrored locally to ensure the deliverables remain self-contained. Key directories:

- `data/` — Source dataset (`fake_property_data_new.json`) and the business field mapping workbook (`Field Config.xlsx`).
- `docs/` — Design notes and implementation planning artifacts.
- `scripts/` — CLI entry points to run ETL workflows or utilities.
- `src/` — Python package containing reusable ETL components, config, and domain models.
- `sql/` — DDL and data quality SQL assets for the normalized MySQL schema.

## Prerequisites

- Python 3.11 (project uses a local virtual environment at `.venv/`).
- Docker Desktop (required to run the provided MySQL Compose stack).
- MySQL client (optional but useful for validation queries).

```powershell
# bootstrap the virtual environment (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Database Setup

1. Launch the base MySQL instance provided by the assessment skeleton:

	```powershell
	docker-compose -f docker-compose.initial.yml up --build -d
	```

	Credentials are embedded in the Compose file and match the defaults consumed by the ETL (`db_user` / `6equj5_db_user`).

2. Apply the normalized schema:

	```powershell
	mysql -h 127.0.0.1 -P 3306 -u db_user -p6equj5_db_user home_db < sql/01_create_schema.sql
	```

## Running the ETL Pipeline

The main entry-point is `scripts/run_etl.py`. It ingests the relaxed JSON payload (parsed with PyYAML to accommodate loosely formatted values), normalizes records with Pydantic validation, and upserts into MySQL via SQLAlchemy.

Dry-run (transforms only):

```powershell
& ".venv/Scripts/python.exe" scripts/run_etl.py --dry-run
```

Full load (writes into MySQL):

```powershell
& ".venv/Scripts/python.exe" scripts/run_etl.py
```

Useful overrides:

- `--data-path` / `--field-config` to point at alternative inputs.
- `--mysql-host`, `--mysql-port`, `--mysql-user`, `--mysql-password`, `--mysql-database` for non-default database targets.
- `--echo-sql` to print SQL issued by SQLAlchemy.

## Normalized Schema Summary

| Table | Grain | Highlights |
| --- | --- | --- |
| `property` | 1 row per unique property | Cleansed address + physical attributes, deterministic `property_key` hashed from address, audit timestamp. |
| `leads` | 1:1 with property | Sales funnel status, reviewer, yield/IRR. |
| `valuation` | 1:N per property | Multi-scenario valuations (list price, rent expectations, comps). |
| `rehab` | 1:N per property | Rehab cost scenarios with boolean condition flags. |
| `hoa` | 1:N per property | HOA dues scenarios with on/off flags. |
| `taxes` | 1:1 per property | Annual tax snapshot. |

All child tables enforce referential integrity with cascading deletes to maintain consistency on reloads.

## Data Quality & Validation

- Pydantic models coerce messy numeric tokens (e.g., `"9191 sqfts"`, word-based numerics) and boolean strings to canonical types.
- Address-derived `property_key` prevents duplicates and supports idempotent reloads.
- Batch inserts exclude null-only payloads (e.g., missing HOA entries) to keep child tables compact.
- `sql/` folder can be extended with additional QA queries (row counts, null checks) as needed.

## Operational Notes

- The raw dataset contains JSON-like content with trailing text tokens; PyYAML handles parsing without manual preprocessing.
- Configuration is centralized in `src/config.py` and can be overridden via environment variables prefixed with `ETL_` (leveraging `pydantic-settings`).
- `docs/implementation_plan.md` tracks the broader work breakdown and can be updated with retrospective notes after execution.

## Next Improvements

1. Add pytest-based regression tests around the transformer to guard against schema drift.
2. Introduce incremental load support (e.g., upsert semantics keyed by `property_key`).
3. Expand SQL data quality scripts (uniqueness checks, distribution profiling) and wire them into CI.

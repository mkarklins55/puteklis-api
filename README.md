# puteklis-api

[![CI](https://github.com/mkarklins55/puteklis-api/actions/workflows/ci.yml/badge.svg)](https://github.com/mkarklins55/puteklis-api/actions/workflows/ci.yml)

Portfolio project: Django/DRF admin + API for Puteklis music data, with sync to the static site files.

Highlights:
- Admin panel for managing songs (Draft/Published)
- Public API (published only) + health check
- Sync to `songs.json`, `songs_data.js`, and `datori.html`
- PostgreSQL local setup with index/EXPLAIN demo
- GitHub Actions CI for automated tests on push/PR
- k3d mini-demo verified (health endpoint returns 200)
- GHCR Docker image published on push to main

Local dev quickstart:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
```

Admin: `http://127.0.0.1:8000/admin/`  
API: `http://127.0.0.1:8000/api/songs/`  
Health: `http://127.0.0.1:8000/api/health/`
Docs: `http://127.0.0.1:8000/api/docs/`

Container image (GHCR):

```bash
docker pull ghcr.io/mkarklins55/puteklis-api:latest
docker run --rm -p 8000:8000 ghcr.io/mkarklins55/puteklis-api:latest
```

Environment:

- Copy `.env.example` to `.env` and set real values.
- `DJANGO_SECRET_KEY` and `DB_PASSWORD` must be set in `.env`.

Docs:

- Local ops runbook: `docs/local_ops.md`
- Transactions and migrations: `docs/transactions_migrations.md`
- Deployment outline (WSL2 demo): `docs/deployment_outline.md`
- Kubernetes mini-demo: `docs/k8s_demo.md`

PostgreSQL (local) setup:

1) Install PostgreSQL 16 and ensure service `postgresql-x64-16` is running.
2) Create DB and user:

```bash
$env:PGPASSWORD='<postgres_password>'
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d postgres -c "CREATE DATABASE puteklis_api;"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d postgres -c "CREATE USER puteklis_user WITH PASSWORD '<db_password>';"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE puteklis_api TO puteklis_user;"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d puteklis_api -c "GRANT ALL ON SCHEMA public TO puteklis_user;"
```

3) Install driver and migrate:

```bash
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
```

4) Import existing songs from `puteklis_weblapa\songs.json`:

```bash
.venv\Scripts\python manage.py import_songs
```

Note: secrets live in `.env` (not committed).

Indexing and query demo (PostgreSQL):

```bash
$env:PGPASSWORD='<postgres_password>'
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d puteklis_api -c "EXPLAIN ANALYZE SELECT * FROM music_song WHERE status = 'published' ORDER BY published_at DESC LIMIT 20;"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d puteklis_api -c \"CREATE INDEX IF NOT EXISTS music_song_status_published_at_idx ON music_song (status, published_at DESC);\"
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -p 5432 -d puteklis_api -c "EXPLAIN ANALYZE SELECT * FROM music_song WHERE status = 'published' ORDER BY published_at DESC LIMIT 20;"
```

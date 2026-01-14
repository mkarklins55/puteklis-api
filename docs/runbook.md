# Runbook (Local + GHCR)

This runbook captures the minimal steps to operate the project locally and verify
the key endpoints.

## Prerequisites
- Python 3.12+
- Docker Desktop (WSL integration enabled)
- PostgreSQL running locally (Windows service)

## Local app (runserver)
```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py createsuperuser
.venv\Scripts\python manage.py runserver
```

Verify:
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/api/health/`
- `http://127.0.0.1:8000/api/metrics/`

## Docker (GHCR image)
```bash
docker pull ghcr.io/mkarklins55/puteklis-api:latest
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY='change-me' \
  -e DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1' \
  -e DB_ENGINE='django.db.backends.postgresql' \
  -e DB_NAME='puteklis_api' \
  -e DB_USER='puteklis_user' \
  -e DB_PASSWORD='replace-me' \
  -e DB_HOST='host.docker.internal' \
  -e DB_PORT='5432' \
  ghcr.io/mkarklins55/puteklis-api:latest
```

Verify:
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/api/health/`
- `http://127.0.0.1:8000/api/metrics/`
- `http://127.0.0.1:8000/api/docs/`

## Troubleshooting
- **Admin is unstyled:** ensure WhiteNoise is enabled and `collectstatic` runs in the Docker build.
- **Port 8000 already in use:** stop the old container (`docker ps`, `docker stop <id>`) or map to `-p 8001:8000`.
- **DB connection fails:** confirm `DB_HOST` and `DB_PASSWORD`, and that PostgreSQL is running.

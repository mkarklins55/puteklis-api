# Local ops runbook

## Start

Run the local development server so you can use the admin UI and API.

```bash
.venv\Scripts\python manage.py runserver
```

Admin: `http://127.0.0.1:8000/admin/`  
API: `http://127.0.0.1:8000/api/songs/`  
Health: `http://127.0.0.1:8000/api/health/`

## Migrations

Create and apply database schema changes when models change.

```bash
.venv\Scripts\python manage.py makemigrations
.venv\Scripts\python manage.py migrate
```

## Import songs

Populate the database from the existing `songs.json`.

```bash
.venv\Scripts\python manage.py import_songs
```

## Sync to puteklis_weblapa

Push selected changes from Django into the static site files.

- Use admin actions:
  - "Sinhronizēt izvēlētās dziesmas"
  - "Sinhronizēt visas dziesmas"

## Fix media names

Align DB file names with the originals from `puteklis_weblapa`.

```bash
.venv\Scripts\python manage.py fix_media_names
```

## Logs

Review sync results and missing file warnings.

- Sync log: `puteklis-api\sync.log`

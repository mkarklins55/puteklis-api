# Transactions and migrations

## Transactions (PostgreSQL)

- A transaction groups multiple SQL statements into one atomic unit.
- Use `BEGIN ... COMMIT` to apply changes, or `ROLLBACK` to undo.
- Django wraps each HTTP request in an implicit transaction when `ATOMIC_REQUESTS` is enabled.
- For critical blocks, use `transaction.atomic()` to guarantee all-or-nothing writes.

Example (psql):

```sql
BEGIN;
UPDATE music_song SET status = 'published' WHERE id = 1;
INSERT INTO audit_log (action, created_at) VALUES ('publish', NOW());
COMMIT;
```

## Migrations (Django)

- Migrations are versioned schema changes generated from model updates.
- Create migrations with:
  - `python manage.py makemigrations`
- Apply them with:
  - `python manage.py migrate`
- Django stores applied migrations in the `django_migrations` table.
- If a migration fails, the DB is left unchanged because it runs inside a transaction.

Tip:
- Keep migrations small and focused.
- Review generated SQL using `python manage.py sqlmigrate app_name 0001`.

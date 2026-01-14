# Release Checklist

Use this checklist before cutting a tagged release and publishing the Docker image.

## Pre-release
- [ ] `git status` is clean.
- [ ] CI is green on `main`.
- [ ] Docker image builds successfully (GHCR workflow).
- [ ] `/api/health/` returns `{"status":"ok"}`.
- [ ] `/api/metrics/` returns counts.
- [ ] `/api/docs/` loads.
- [ ] Admin UI renders correctly (CSS/JS).
- [ ] Secrets are not committed (`.env` stays local).

## Tag release
```bash
git tag v1.0.0
git push origin v1.0.0
```

## Post-release
- [ ] GHCR shows the new tag (e.g., `v1.0.0`).
- [ ] `docker pull ghcr.io/mkarklins55/puteklis-api:v1.0.0` works.
- [ ] Smoke test the image on port 8000.

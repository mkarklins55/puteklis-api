# Docker + systemd (WSL) demo

This shows how to run the GHCR image as a managed systemd service in WSL.

## 1) Create env file
Create `/etc/puteklis-api.env` with your real values:

```
DJANGO_SECRET_KEY=change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=puteklis_api
DB_USER=puteklis_user
DB_PASSWORD=replace-me
DB_HOST=host.docker.internal
DB_PORT=5432
```

## 2) Create systemd unit
Create `/etc/systemd/system/puteklis-api.service`:

```
[Unit]
Description=Puteklis API (Docker)
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=/etc/puteklis-api.env
ExecStart=/usr/bin/docker run --rm --name puteklis-api -p 8000:8000 \
  -e DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} \
  -e DJANGO_ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS} \
  -e DB_ENGINE=${DB_ENGINE} \
  -e DB_NAME=${DB_NAME} \
  -e DB_USER=${DB_USER} \
  -e DB_PASSWORD=${DB_PASSWORD} \
  -e DB_HOST=${DB_HOST} \
  -e DB_PORT=${DB_PORT} \
  ghcr.io/mkarklins55/puteklis-api:latest
ExecStop=/usr/bin/docker stop puteklis-api
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## 3) Enable and start

```
sudo systemctl daemon-reload
sudo systemctl enable puteklis-api.service
sudo systemctl start puteklis-api.service
sudo systemctl status puteklis-api.service --no-pager
```

## 4) Verify
- `http://127.0.0.1:8000/api/health/`
- `http://127.0.0.1:8000/api/metrics/`
- `http://127.0.0.1:8000/admin/`

## Logs

```
journalctl -u puteklis-api.service -f
```

## Stop

```
sudo systemctl stop puteklis-api.service
```

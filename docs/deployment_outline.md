# Deployment outline (WSL2 demo)

This is a local WSL2 walkthrough showing a typical production stack:
gunicorn + nginx + systemd.

## System packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

## App setup

```bash
cd /mnt/c/Users/mkark/Documents/GitHub/puteklis-api
python3 -m venv .venv
. .venv/bin/activate
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install gunicorn
```

## systemd unit (gunicorn)

```bash
sudo tee /etc/systemd/system/gunicorn-puteklis.socket > /dev/null <<'EOF'
[Unit]
Description=gunicorn socket for puteklis-api

[Socket]
ListenStream=/run/gunicorn-puteklis.sock

[Install]
WantedBy=sockets.target
EOF
```

```bash
sudo tee /etc/systemd/system/gunicorn-puteklis.service > /dev/null <<'EOF'
[Unit]
Description=gunicorn service for puteklis-api
Requires=gunicorn-puteklis.socket
After=network.target

[Service]
User=mkark
Group=www-data
WorkingDirectory=/mnt/c/Users/mkark/Documents/GitHub/puteklis-api
EnvironmentFile=/mnt/c/Users/mkark/Documents/GitHub/puteklis-api/.env
ExecStart=/mnt/c/Users/mkark/Documents/GitHub/puteklis-api/.venv/bin/gunicorn \
  --access-logfile - --error-logfile - \
  --workers 3 --bind unix:/run/gunicorn-puteklis.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-puteklis.socket
sudo systemctl restart gunicorn-puteklis.service
```

## nginx reverse proxy

```bash
sudo tee /etc/nginx/sites-available/puteklis-api > /dev/null <<'EOF'
server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://unix:/run/gunicorn-puteklis.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/puteklis-api /etc/nginx/sites-enabled/puteklis-api
sudo nginx -t
sudo systemctl restart nginx
```

## Verify

```bash
curl -i http://localhost/api/health/
```

Expected: HTTP 200 with `{"status":"ok"}`.

#!/usr/bin/env bash

set -euo pipefail

APP_DIR="/opt/confessions_board"
REPO_URL="https://github.com/<your-username>/<your-repo>.git"

echo 
sudo apt update && sudo apt upgrade -y

echo 
sudo apt install -y python3-venv python3-pip postgresql postgresql-contrib git

echo 
sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

echo 
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo 
sudo -u postgres psql -c "CREATE DATABASE confessions_db;" || true
sudo -u postgres psql -c "CREATE USER confessions_user WITH PASSWORD 'change-me';" || true
sudo -u postgres psql -c "ALTER ROLE confessions_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE confessions_db TO confessions_user;"

echo 
cp .env.example .env
echo 

echo 
python manage.py migrate
python manage.py collectstatic --noinput

echo 
sudo mkdir -p /var/log/confessions
sudo chown "$USER":www-data /var/log/confessions

echo 
sudo cp deploy/confessions.service /etc/systemd/system/confessions.service
sudo systemctl daemon-reload
sudo systemctl enable confessions
sudo systemctl start confessions

echo 

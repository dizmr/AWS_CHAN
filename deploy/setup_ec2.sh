#!/usr/bin/env bash
# Одноразовий скрипт первинного налаштування EC2-інстансу (Ubuntu 22.04/24.04).
# Запускати вручну після підключення по SSH:
#   chmod +x deploy/setup_ec2.sh && ./deploy/setup_ec2.sh
set -euo pipefail

APP_DIR="/opt/confessions_board"
REPO_URL="https://github.com/<your-username>/<your-repo>.git"

echo ">>> Оновлення пакетів"
sudo apt update && sudo apt upgrade -y

echo ">>> Встановлення Python, PostgreSQL, git"
sudo apt install -y python3-venv python3-pip postgresql postgresql-contrib git

echo ">>> Клонування репозиторію"
sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

echo ">>> Створення віртуального середовища"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> Налаштування бази даних PostgreSQL"
sudo -u postgres psql -c "CREATE DATABASE confessions_db;" || true
sudo -u postgres psql -c "CREATE USER confessions_user WITH PASSWORD 'change-me';" || true
sudo -u postgres psql -c "ALTER ROLE confessions_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE confessions_db TO confessions_user;"

echo ">>> Створіть файл .env на основі .env.example"
cp .env.example .env
echo "Відредагуйте $APP_DIR/.env перед продовженням (SECRET_KEY, паролі тощо)."

echo ">>> Міграції та статичні файли"
python manage.py migrate
python manage.py collectstatic --noinput

echo ">>> Налаштування логів"
sudo mkdir -p /var/log/confessions
sudo chown "$USER":www-data /var/log/confessions

echo ">>> Встановлення systemd-сервісу"
sudo cp deploy/confessions.service /etc/systemd/system/confessions.service
sudo systemctl daemon-reload
sudo systemctl enable confessions
sudo systemctl start confessions

echo ">>> Готово! Перевірте статус: sudo systemctl status confessions"

# 🕯️ Дошка анонімних зізнань

Веб-додаток у стилі анонімних записок: користувачі залишають короткі
записи без реєстрації. Кожен новий запис отримує статус **"на
перевірці"** і публікується лише після автоматичної перевірки на
заборонені слова. Опубліковані записи мають лічильники переглядів і
лайків.

Фінальний проєкт курсу «Створення хмарних рішень з використанням AWS».

## Стек

- **Backend:** Django 5
- **База даних:** PostgreSQL, розгорнута безпосередньо на EC2-інстансі
- **WSGI-сервер:** Gunicorn
- **Статика:** WhiteNoise
- **Хмара:** AWS EC2

## Логіка станів запису

```
[користувач надсилає форму]
            │
            ▼
        PENDING  (на перевірці)
            │
   автоматична перевірка тексту
   на заборонені слова (moderation.py)
            │
   ┌────────┴────────┐
   ▼                  ▼
APPROVED           REJECTED
(видно у стрічці)  (приховано,
                    видно лише в адмінці)
```

Перевірка виконується синхронно одразу після створення запису
(`board/moderation.py`), список заборонених слів налаштовується через
змінну середовища `BANNED_WORDS` без зміни коду.

## Використані AWS-сервіси

| Сервіс | Призначення |
|---|---|
| **EC2** | Хостинг застосунку (Django + Gunicorn + PostgreSQL на одному інстансі) |
| **Security Groups** | Обмеження вхідного трафіку (порти 22, 80/443) |
| **(опційно) Elastic IP** | Стала публічна адреса інстансу |
| **(опційно) IAM** | Обмежений доступ для деплойного користувача/ключа |

## Структура репозиторію

```
confessions_board/
├── config/                # Django-проєкт (settings, urls, wsgi)
├── board/                 # Застосунок: моделі, views, шаблони, модерація
├── deploy/
│   ├── confessions.service   # systemd-юніт
│   └── setup_ec2.sh          # скрипт первинного налаштування EC2
├── .github/workflows/deploy.yml  # автодеплой при пуші у main
├── requirements.txt
├── .env.example
└── .gitignore
```

## Розгортання на EC2

### 1. Підготовка EC2

1. Створіть інстанс (Ubuntu 22.04/24.04, t2.micro/t3.micro достатньо).
2. У Security Group відкрийте порти `22` (SSH) та `80`/`8000` (HTTP).
3. Підключіться по SSH:
   ```bash
   ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```

### 2. Клонування та встановлення

```bash
git clone https://github.com/<your-username>/<your-repo>.git /opt/confessions_board
cd /opt/confessions_board
chmod +x deploy/setup_ec2.sh
./deploy/setup_ec2.sh
```

Скрипт `setup_ec2.sh`:
- встановлює Python, PostgreSQL, git;
- створює віртуальне середовище і ставить залежності;
- створює базу даних і користувача PostgreSQL;
- копіює `.env.example` → `.env` (відредагуйте його своїми значеннями);
- застосовує міграції, збирає статику;
- встановлює та вмикає `systemd`-сервіс.

### 3. Змінні середовища

Усі чутливі дані зберігаються у `/opt/confessions_board/.env`
(файл **не** потрапляє у git, див. `.gitignore`) і підключаються у
`deploy/confessions.service` через `EnvironmentFile=`:

```env
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=your-ec2-ip,your-domain.com
DB_NAME=confessions_db
DB_USER=confessions_user
DB_PASSWORD=...
DB_HOST=127.0.0.1
DB_PORT=5432
```

### 4. systemd

```bash
sudo systemctl status confessions   # перевірити статус
sudo systemctl restart confessions  # перезапустити після оновлення коду
sudo systemctl enable confessions   # автозапуск при перезавантаженні (вже виконано скриптом)
```

### 5. Автодеплой через GitHub Actions

Workflow `.github/workflows/deploy.yml` при кожному пуші у `main`
підключається по SSH до EC2, робить `git pull`, оновлює залежності,
застосовує міграції та перезапускає сервіс.

У налаштуваннях репозиторію (**Settings → Secrets and variables →
Actions**) додайте:

| Secret | Значення |
|---|---|
| `EC2_HOST` | публічний IP або домен EC2-інстансу |
| `EC2_USER` | зазвичай `ubuntu` |
| `EC2_SSH_KEY` | приватний SSH-ключ (вміст `.pem`-файлу) |
| `EC2_PORT` | зазвичай `22` |

## Локальний запуск (для розробки)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # і відредагуйте значення
python manage.py migrate
python manage.py runserver
```

## Адмін-панель

`/admin/` — перегляд усіх записів (включно з `PENDING`/`REJECTED`),
керування статусами вручну:

```bash
python manage.py createsuperuser
```

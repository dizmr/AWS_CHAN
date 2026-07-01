

# дошка анонімних зізнань

веб-додаток де можна залишити анонімний запис без реєстрації.
новий запис іде в статус "на перевірці", автоматично перевіряється
на заборонені слова і або публікується, або ховається.
опубліковані записи мають лічильник переглядів і лайків.

## стек
- django + gunicorn
- postgresql на тому ж EC2
- systemd для автозапуску (systemctl enable)
- .env для секретів, підключається через EnvironmentFile
- github actions для автодеплою на пуш в main

## aws сервіси
- EC2 — все крутиться на одному інстансі
- security group — відкриті порти 22 і 8000

## як задеплоїти
1. клонуємо репо на EC2 в /opt/confessions_board
2. ставимо залежності з requirements.txt в venv
3. заповнюємо .env (secret key, allowed hosts = публічний ip, дані бд)
4. python manage.py migrate
5. копіюємо deploy/confessions.service в /etc/systemd/system/
6. systemctl daemon-reload && systemctl enable confessions && systemctl start confessions

сайт піднімається на http://<public-ip>:8000
